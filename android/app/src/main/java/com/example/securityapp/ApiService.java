package com.example.securityapp;

import retrofit2.Call;
import retrofit2.http.Body;
import java.util.List;
import retrofit2.http.Header;
import retrofit2.http.POST;

public interface ApiService {

    @POST("apps/")
    Call<App> createApp(@Header("X-API-KEY") String apiKey, @Body App app);

    @POST("apps/bulk")
    Call<List<App>> createApps(@Header("X-API-KEY") String apiKey, @Body AppBulkCreate apps);

    @POST("token")
    Call<Token> login(@Body User user);

    @POST("screenshots/")
    Call<Void> createScreenshot(@Header("X-API-KEY") String apiKey, @Body Screenshot screenshot);
}
