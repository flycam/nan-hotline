package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;

import org.cacert.gigi.output.template.Outputable;

public class WizardCall extends Action {
    private String supporteeSIPURI;
    private Phone supporterPhone = null;
    private String path;

    public WizardCall(ResultSet res) throws SQLException {
        super(res);
        this.supporteeSIPURI = res.getString("supportee_sip_uri");
        this.path = res.getString("path");
        int supporter = res.getInt("supporter_phone");
        if (supporter != 0) {
            this.supporterPhone = Phone.getById(supporter);
        }
    }

    @Override
    public Outputable output(Map<String, Object> vars) {
        vars.put("path", path);
        System.out.println(supporterPhone);
        vars.put("supporter",
                supporterPhone != null ? supporterPhone.getSipUri() : null);
        vars.put("supportee", supporteeSIPURI);
        return getDefaultTemplate();
    }

}