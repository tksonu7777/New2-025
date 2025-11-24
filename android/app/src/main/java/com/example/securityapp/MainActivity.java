package com.example.securityapp;

import android.content.Intent;
import androidx.appcompat.app.AppCompatActivity;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.util.Base64;
import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKeys;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.GeneralSecurityException;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {

    private ApiService apiService;
    private String apiKey;
    private AppAdapter appAdapter;
    private List<App> appList = new ArrayList<>();
    private ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        try {
            String masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC);
            SharedPreferences sharedPreferences = EncryptedSharedPreferences.create(
                    "secret_shared_prefs",
                    masterKeyAlias,
                    getApplicationContext(),
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            );
            apiKey = sharedPreferences.getString("API_KEY", null);
        } catch (GeneralSecurityException | IOException e) {
            e.printStackTrace();
        }

        if (apiKey == null) {
            Intent intent = new Intent(MainActivity.this, LoginActivity.class);
            startActivity(intent);
            finish();
            return;
        }

        RecyclerView recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        appAdapter = new AppAdapter(appList);
        recyclerView.setAdapter(appAdapter);

        progressBar = findViewById(R.id.progressBar);

        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(BuildConfig.BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        apiService = retrofit.create(ApiService.class);

        Button scanButton = findViewById(R.id.scanButton);
        scanButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                scanInstalledApps();
            }
        });

        Button screenshotButton = findViewById(R.id.screenshotButton);
        screenshotButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                takeAndUploadScreenshot();
            }
        });
    }

    private void takeAndUploadScreenshot() {
        Bitmap screenshotBitmap = takeScreenshot();
        if (screenshotBitmap != null) {
            String hash = calculateAverageHash(screenshotBitmap);
            String appName = getApplicationInfo().loadLabel(getPackageManager()).toString();

            Screenshot screenshot = new Screenshot(hash, appName);

            apiService.createScreenshot(apiKey, screenshot).enqueue(new Callback<Void>() {
                @Override
                public void onResponse(Call<Void> call, Response<Void> response) {
                    if (response.isSuccessful()) {
                        Toast.makeText(MainActivity.this, "Screenshot uploaded successfully", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this, "Screenshot upload failed: " + response.message(), Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<Void> call, Throwable t) {
                    Toast.makeText(MainActivity.this, "Screenshot upload failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        } else {
            Toast.makeText(MainActivity.this, "Failed to take screenshot", Toast.LENGTH_SHORT).show();
        }
    }

    private Bitmap takeScreenshot() {
        View rootView = getWindow().getDecorView().getRootView();
        rootView.setDrawingCacheEnabled(true);
        Bitmap bitmap = Bitmap.createBitmap(rootView.getDrawingCache());
        rootView.setDrawingCacheEnabled(false);
        return bitmap;
    }

    private String calculateAverageHash(Bitmap bitmap) {
        Bitmap resizedBitmap = Bitmap.createScaledBitmap(bitmap, 8, 8, true);
        long sum = 0;
        int[] pixels = new int[64];
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                int pixel = resizedBitmap.getPixel(j, i);
                int grayscale = (int) (0.299 * ((pixel >> 16) & 0xFF) +
                                       0.587 * ((pixel >> 8) & 0xFF) +
                                       0.114 * (pixel & 0xFF));
                pixels[i * 8 + j] = grayscale;
                sum += grayscale;
            }
        }
        long average = sum / 64;
        StringBuilder hash = new StringBuilder();
        for (int pixel : pixels) {
            if (pixel > average) {
                hash.append('1');
            } else {
                hash.append('0');
            }
        }
        StringBuilder hexHash = new StringBuilder();
        for (int i = 0; i < hash.length(); i += 4) {
            String fourBits = hash.substring(i, i + 4);
            int decimal = Integer.parseInt(fourBits, 2);
            hexHash.append(Integer.toHexString(decimal));
        }
        return hexHash.toString();
    }

    private void scanInstalledApps() {
        progressBar.setVisibility(View.VISIBLE);
        appList.clear();
        appAdapter.notifyDataSetChanged();
        PackageManager pm = getPackageManager();
        List<ApplicationInfo> apps = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        List<App> appsToCreate = new ArrayList<>();

        for (ApplicationInfo appInfo : apps) {
            String appName = appInfo.loadLabel(pm).toString();
            String packageName = appInfo.packageName;
            String iconB64 = getIconB64(appInfo.loadIcon(pm));
            appsToCreate.add(new App(appName, packageName, iconB64));
        }

        AppBulkCreate appBulkCreate = new AppBulkCreate(appsToCreate);
        apiService.createApps(apiKey, appBulkCreate).enqueue(new Callback<List<App>>() {
            @Override
            public void onResponse(Call<List<App>> call, Response<List<App>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful()) {
                    appList.addAll(response.body());
                    appAdapter.notifyDataSetChanged();
                } else {
                    Toast.makeText(MainActivity.this, "Scan failed: " + response.message(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<List<App>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                Toast.makeText(MainActivity.this, "Scan failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private String getIconB64(Drawable drawable) {
        if (drawable instanceof BitmapDrawable) {
            Bitmap bitmap = ((BitmapDrawable) drawable).getBitmap();
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            return Base64.encodeToString(byteArray, Base64.DEFAULT);
        }
        return null;
    }
}
