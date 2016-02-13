package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;

import me.streib.janis.nanhotline.web.pages.Page;

import org.cacert.gigi.output.template.Outputable;

public class MergeAction extends Action {
    private int oldCase;

    public MergeAction(ResultSet res) throws SQLException {
        super(res);
        this.oldCase = res.getInt("old_case");
    }

    @Override
    public Outputable output(Map<String, Object> vars, Supporter user)
            throws SQLException {
        vars.put("time", Page.DE_FROMAT_DATE.format(getTime()));
        vars.put("old_case", oldCase);
        return getDefaultTemplate();
    }

}
