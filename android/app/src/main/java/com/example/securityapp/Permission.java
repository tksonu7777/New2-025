package com.example.securityapp;

import com.google.gson.annotations.SerializedName;

public class Permission {
    private String name;
    @SerializedName("is_hidden")
    private boolean isHidden;

    public String getName() {
        return name;
    }

    public boolean isHidden() {
        return isHidden;
    }
}
