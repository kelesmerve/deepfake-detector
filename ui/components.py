def _as_pct(value):
    return value * 100 if isinstance(value, float) and value <= 1 else value


def _distribution_bars(real_pct, fake_pct):
    real_pct = max(0, min(100, real_pct))
    fake_pct = max(0, min(100, fake_pct))
    return f"""
            <div style="
                margin: 18px auto 0 auto;
                max-width: 440px;
                background: rgba(255,255,255,0.72);
                border: 1px solid rgba(148,163,184,0.28);
                border-radius: 12px;
                padding: 14px;
                text-align: left;
            ">
                <div style="font-size: 13px; font-weight: 800; color: #475467; margin-bottom: 10px;">Confidence Distribution</div>
                <div style="display:flex; align-items:center; gap:10px; margin-bottom: 10px;">
                    <div style="width:58px; color:#15803d; font-size:13px; font-weight:800;">Real</div>
                    <div style="flex:1; height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden;">
                        <div style="width:{real_pct:.1f}%; height:100%; background:linear-gradient(90deg,#16a34a,#86efac); border-radius:999px;"></div>
                    </div>
                    <div style="width:54px; text-align:right; color:#15803d; font-size:13px; font-weight:800;">{real_pct:.1f}%</div>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:58px; color:#dc2626; font-size:13px; font-weight:800;">Fake</div>
                    <div style="flex:1; height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden;">
                        <div style="width:{fake_pct:.1f}%; height:100%; background:linear-gradient(90deg,#ef4444,#fb7185); border-radius:999px;"></div>
                    </div>
                    <div style="width:54px; text-align:right; color:#dc2626; font-size:13px; font-weight:800;">{fake_pct:.1f}%</div>
                </div>
            </div>
    """


def format_verdict(status, confidence, real_prob=None, fake_prob=None):
    """Generate styled HTML verdict banner."""
    conf_pct = _as_pct(confidence)
    if real_prob is None or fake_prob is None:
        if status == "real":
            real_pct = conf_pct
            fake_pct = 100 - conf_pct
        elif status == "fake":
            fake_pct = conf_pct
            real_pct = 100 - conf_pct
        else:
            real_pct = fake_pct = 0
    else:
        real_pct = _as_pct(real_prob)
        fake_pct = _as_pct(fake_prob)
    distribution_html = _distribution_bars(real_pct, fake_pct) if status in {"fake", "real"} else ""

    if status == "fake":
        if conf_pct > 85:
            risk_label, risk_color = "CRITICAL", "#dc2626"
        elif conf_pct > 70:
            risk_label, risk_color = "HIGH", "#ea580c"
        elif conf_pct > 55:
            risk_label, risk_color = "MEDIUM", "#ca8a04"
        else:
            risk_label, risk_color = "LOW", "#64748b"

        return f"""
        <div style="
            background: #fff7f7;
            border: 1px solid #fecaca;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 10px 26px rgba(220,38,38,0.08);
        ">
            <div style="font-size: 13px; color: #991b1b; margin-bottom: 8px; font-weight: 700;">Detection Result</div>
            <div style="font-size: 32px; font-weight: 800; color: #dc2626; margin-bottom: 16px;">
                DEEPFAKE DETECTED
            </div>
            <div style="
                background: #fee2e2;
                border-radius: 999px;
                height: 14px;
                overflow: hidden;
                margin: 0 auto 12px auto;
                max-width: 400px;
                border: 1px solid #fecaca;
            ">
                <div style="
                    height: 100%;
                    width: {conf_pct:.1f}%;
                    background: linear-gradient(90deg, #ef4444, #fb7185);
                    border-radius: 999px;
                    transition: width 0.8s ease;
                "></div>
            </div>
            <div style="color: #344054; font-size: 17px; font-weight: 650;">
                Confidence: <span style="color: #dc2626;">{conf_pct:.1f}%</span>
            </div>
            {distribution_html}
            <div style="margin-top: 12px;">
                <span style="
                    background: {risk_color}22;
                    color: {risk_color};
                    padding: 6px 18px;
                    border-radius: 999px;
                    font-size: 13px;
                    font-weight: 700;
                    border: 1px solid {risk_color}44;
                ">RISK: {risk_label}</span>
            </div>
        </div>
        """
    elif status == "real":
        return f"""
        <div style="
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 10px 26px rgba(22,163,74,0.08);
        ">
            <div style="font-size: 13px; color: #166534; margin-bottom: 8px; font-weight: 700;">Detection Result</div>
            <div style="font-size: 32px; font-weight: 800; color: #16a34a; margin-bottom: 16px;">
                AUTHENTIC
            </div>
            <div style="
                background: #dcfce7;
                border-radius: 999px;
                height: 14px;
                overflow: hidden;
                margin: 0 auto 12px auto;
                max-width: 400px;
                border: 1px solid #bbf7d0;
            ">
                <div style="
                    height: 100%;
                    width: {conf_pct:.1f}%;
                    background: linear-gradient(90deg, #16a34a, #4ade80);
                    border-radius: 999px;
                    transition: width 0.8s ease;
                "></div>
            </div>
            <div style="color: #344054; font-size: 17px; font-weight: 650;">
                Confidence: <span style="color: #16a34a;">{conf_pct:.1f}%</span>
            </div>
            {distribution_html}
            <div style="margin-top: 12px;">
                <span style="
                    background: rgba(22,163,74,0.12);
                    color: #15803d;
                    padding: 6px 18px;
                    border-radius: 999px;
                    font-size: 13px;
                    font-weight: 700;
                    border: 1px solid rgba(22,163,74,0.24);
                ">RISK: SAFE</span>
            </div>
        </div>
        """
    elif status == "error":
        return """
        <div style="
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        ">
            <div style="font-size: 26px; color: #c2410c; font-weight: 800;">Error</div>
        </div>
        """
    else:
        return """
        <div style="
            background: #f8fbff;
            border: 1px solid #dbeafe;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        ">
            <div style="font-size: 13px; color: #0369a1; margin-bottom: 8px; font-weight: 700;">Awaiting Input</div>
            <div style="font-size: 23px; font-weight: 700; color: #172033;">
                Upload a file to begin analysis
            </div>
        </div>
        """
