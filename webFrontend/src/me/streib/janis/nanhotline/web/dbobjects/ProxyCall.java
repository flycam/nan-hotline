package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;

import me.streib.janis.nanhotline.web.pages.Page;

import org.cacert.gigi.output.template.Outputable;

public class ProxyCall extends Action {
    private String targetSipUri;
    private boolean accepted;
    private Phone supporterPhone;

    public ProxyCall(ResultSet res) throws SQLException {
        super(res);
        this.accepted = res.getBoolean("accepted");
        this.targetSipUri = res.getString("target_sip_uri");
        this.supporterPhone = Phone.getById(res.getInt("supporter_phone"));
    }

    @Override
    public Outputable output(Map<String, Object> vars, Supporter user)
            throws SQLException {
        vars.put("supp_sip", supporterPhone.getSipUri());
        vars.put("supp_name",
                Supporter.getSupporterById(supporterPhone.getSupporter())
                        .getName());
        vars.put("targ_sip", targetSipUri);
        vars.put("accpeted", accepted);
        vars.put("time", Page.DE_FROMAT_DATE.format(getTime()));
        return getDefaultTemplate();
    }
}
