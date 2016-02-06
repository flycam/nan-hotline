package me.streib.janis.nanhotline.web.dbobjects;

import java.io.PrintWriter;
import java.net.URL;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;
import java.util.Map;

import org.cacert.gigi.output.template.Outputable;
import org.cacert.gigi.output.template.Template;

public abstract class Action {
    private Date date;
    private Template defaultTemplate;

    public Action(ResultSet res) throws SQLException {
        this.date = new Date(res.getLong("time"));
        URL resource = getClass().getResource(
                getClass().getSimpleName() + ".templ");
        if (resource != null) {
            defaultTemplate = new Template(resource);
        }
    }

    public Date getTime() {
        return date;
    }

    public abstract Outputable output(PrintWriter out, Map<String, Object> vars);

    protected Template getDefaultTemplate() {
        return defaultTemplate;
    }

}
