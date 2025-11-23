package com.example.securityapp;

import com.google.gson.annotations.SerializedName;

public class ApiCall {
    private String endpoint;
    private String payload;
    @SerializedName("risk_score")
    private int riskScore;
    @SerializedName("is_suspicious")
    private boolean isSuspicious;

    public String getEndpoint() {
        return endpoint;
    }

    public String getPayload() {
        return payload;
    }

    public int getRiskScore() {
        return riskScore;
    }

    public boolean isSuspicious() {
        return isSuspicious;
    }
}
