package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.Map;

import me.streib.janis.nanhotline.web.pages.Page;

import org.cacert.gigi.output.template.IterableDataset;
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
    public Outputable output(Map<String, Object> vars, Supporter user)
            throws SQLException {
        vars.put("path", path);
        vars.put("supporter",
                supporterPhone != null ? supporterPhone.getSipUri() : null);
        vars.put("supportee", supporteeSIPURI);
        vars.put("time", Page.DE_FROMAT_DATE.format(getTime()));
        vars.put("action_id", getId());
        final LinkedList<Phone> supp = user.getPhones();
        vars.put("supp_phones", new IterableDataset() {
            int i = 0;

            @Override
            public boolean next(Map<String, Object> vars) {
                if (i >= supp.size()) {
                    return false;
                }
                Phone p = supp.get(i++);
                vars.put("supp_phone_id", p.getId());
                vars.put("supp_phone", p.getSipUri());
                return true;
            }
        });
        return getDefaultTemplate();
    }

    public String getSupporteeSIPURI() {
        return supporteeSIPURI;
    }

    public Phone getSupporterPhone() {
        return supporterPhone;
    }
}
