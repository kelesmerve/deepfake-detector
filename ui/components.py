def format_verdict(status, confidence):
    """Generate styled HTML verdict banner."""
    conf_pct = confidence * 100 if isinstance(confidence, float) and confidence <= 1 else confidence

    if status == "fake":
        if conf_pct > 85:
            risk_label, risk_color = "CRITICAL", "#ff3366"
        elif conf_pct > 70:
            risk_label, risk_color = "HIGH", "#ff6b35"
        elif conf_pct > 55:
            risk_label, risk_color = "MEDIUM", "#ffd93d"
        else:
            risk_label, risk_color = "LOW", "#888"

        return f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,51,102,0.15) 0%, rgba(139,0,78,0.25) 100%);
            border: 1px solid rgba(255,51,102,0.4);
            border-radius: 16px;
            padding: 28px;
            text-align: center;
        ">
            <div style="font-size: 14px; letter-spacing: 3px; color: #ff6b8a; margin-bottom: 8px; text-transform: uppercase;">Detection Result</div>
            <div style="font-size: 36px; font-weight: 800; color: #ff3366; text-shadow: 0 0 30px rgba(255,51,102,0.5); margin-bottom: 16px;">
                DEEPFAKE DETECTED
            </div>
            <div style="
                background: rgba(0,0,0,0.3);
                border-radius: 999px;
                height: 14px;
                overflow: hidden;
                margin: 0 auto 12px auto;
                max-width: 400px;
                border: 1px solid rgba(255,51,102,0.2);
            ">
                <div style="
                    height: 100%;
                    width: {conf_pct:.1f}%;
                    background: linear-gradient(90deg, #ff3366, #ff6b8a);
                    border-radius: 999px;
                    box-shadow: 0 0 12px rgba(255,51,102,0.6);
                    transition: width 0.8s ease;
                "></div>
            </div>
            <div style="color: #e0e0e0; font-size: 18px; font-weight: 600;">
                Confidence: <span style="color: #ff6b8a;">{conf_pct:.1f}%</span>
            </div>
            <div style="margin-top: 12px;">
                <span style="
                    background: {risk_color}22;
                    color: {risk_color};
                    padding: 6px 18px;
                    border-radius: 999px;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    border: 1px solid {risk_color}44;
                ">RISK: {risk_label}</span>
            </div>
        </div>
        """
    elif status == "real":
        return f"""
        <div style="
            background: linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(6,78,59,0.25) 100%);
            border: 1px solid rgba(16,185,129,0.35);
            border-radius: 16px;
            padding: 28px;
            text-align: center;
        ">
            <div style="font-size: 14px; letter-spacing: 3px; color: #6ee7b7; margin-bottom: 8px; text-transform: uppercase;">Detection Result</div>
            <div style="font-size: 36px; font-weight: 800; color: #10b981; text-shadow: 0 0 30px rgba(16,185,129,0.5); margin-bottom: 16px;">
                AUTHENTIC
            </div>
            <div style="
                background: rgba(0,0,0,0.3);
                border-radius: 999px;
                height: 14px;
                overflow: hidden;
                margin: 0 auto 12px auto;
                max-width: 400px;
                border: 1px solid rgba(16,185,129,0.2);
            ">
                <div style="
                    height: 100%;
                    width: {conf_pct:.1f}%;
                    background: linear-gradient(90deg, #10b981, #6ee7b7);
                    border-radius: 999px;
                    box-shadow: 0 0 12px rgba(16,185,129,0.6);
                    transition: width 0.8s ease;
                "></div>
            </div>
            <div style="color: #e0e0e0; font-size: 18px; font-weight: 600;">
                Confidence: <span style="color: #6ee7b7;">{conf_pct:.1f}%</span>
            </div>
            <div style="margin-top: 12px;">
                <span style="
                    background: rgba(16,185,129,0.15);
                    color: #10b981;
                    padding: 6px 18px;
                    border-radius: 999px;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    border: 1px solid rgba(16,185,129,0.3);
                ">RISK: SAFE</span>
            </div>
        </div>
        """
    elif status == "error":
        return """
        <div style="
            background: rgba(255,100,100,0.1);
            border: 1px solid rgba(255,100,100,0.3);
            border-radius: 16px;
            padding: 28px;
            text-align: center;
        ">
            <div style="font-size: 28px; color: #ff6b6b;">Error</div>
        </div>
        """
    else:
        return """
        <div style="
            background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(88,28,135,0.15) 100%);
            border: 1px solid rgba(139,92,246,0.2);
            border-radius: 16px;
            padding: 28px;
            text-align: center;
        ">
            <div style="font-size: 14px; letter-spacing: 3px; color: #a78bfa; margin-bottom: 8px; text-transform: uppercase;">Awaiting Input</div>
            <div style="font-size: 24px; font-weight: 600; color: #c4b5fd;">
                Upload a file to begin analysis
            </div>
        </div>
        """