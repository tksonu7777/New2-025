package com.example.securityapp;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class App {
    private String name;
    @SerializedName("package_name")
    private String packageName;
    @SerializedName("is_clone")
    private boolean isClone;
    @SerializedName("is_fake")
    private boolean isFake;
    @SerializedName("icon_hash")
    private String iconHash;
    @SerializedName("icon_b64")
    private String iconB64;
    private List<Permission> permissions;
    @SerializedName("api_calls")
    private List<ApiCall> apiCalls;

    public App(String name, String packageName, String iconB64) {
        this.name = name;
        this.packageName = packageName;
        this.iconB64 = iconB64;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPackageName() {
        return packageName;
    }

    public void setPackageName(String packageName) {
        this.packageName = packageName;
    }

    public boolean isClone() {
        return isClone;
    }

    public boolean isFake() {
        return isFake;
    }

    public String getIconHash() {
        return iconHash;
    }

    public List<Permission> getPermissions() {
        return permissions;
    }

    public List<ApiCall> getApiCalls() {
        return apiCalls;
    }
}
