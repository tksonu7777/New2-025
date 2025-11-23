package com.example.securityapp;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class AppAdapter extends RecyclerView.Adapter<AppAdapter.ViewHolder> {

    private List<App> appList;

    public AppAdapter(List<App> appList) {
        this.appList = appList;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.list_item_app, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        App app = appList.get(position);
        holder.appName.setText(app.getName());
        holder.packageName.setText(app.getPackageName());
        String status = "";
        if (app.isClone()) {
            status += "Clone ";
        }
        if (app.isFake()) {
            status += "Fake";
        }
        holder.status.setText(status);
    }

    @Override
    public int getItemCount() {
        return appList.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        public TextView appName;
        public TextView packageName;
        public TextView status;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            appName = itemView.findViewById(R.id.appName);
            packageName = itemView.findViewById(R.id.packageName);
            status = itemView.findViewById(R.id.status);
        }
    }
}
