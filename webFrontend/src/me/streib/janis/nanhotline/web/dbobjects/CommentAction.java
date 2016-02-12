package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;

import me.streib.janis.nanhotline.web.pages.Page;

import org.cacert.gigi.output.template.Outputable;

public class CommentAction extends Action {

    private String commentText;
    private Supporter supp;

    public CommentAction(ResultSet res) throws SQLException {
        super(res);
        this.commentText = res.getString("comment");
        this.supp = Supporter.getSupporterById(res.getInt("supporter"));
    }

    @Override
    public Outputable output(Map<String, Object> vars, Supporter user) {
        vars.put("comment", commentText);
        vars.put("time", Page.DE_FROMAT_DATE.format(getTime()));
        vars.put("supporter", supp.getName());
        return getDefaultTemplate();
    }

}
