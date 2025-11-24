package com.example.securityapp;

public class Screenshot {
    private String hash;
    private String app_name;

    public Screenshot(String hash, String app_name) {
        this.hash = hash;
        this.app_name = app_name;
    }

    public String getHash() {
        return hash;
    }

    public String getAppName() {
        return app_name;
    }
}
