package me.streib.janis.nanhotline.web.dbobjects;

import java.net.URL;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;
import java.util.LinkedList;
import java.util.Map;

import me.streib.janis.nanhotline.web.DatabaseConnection;

import org.cacert.gigi.output.template.Outputable;
import org.cacert.gigi.output.template.Template;
import org.eclipse.jetty.util.log.Log;

public abstract class Action {
    private Date date;
    private Template defaultTemplate;
    private int id, caseId;

    public static Action getById(int id) throws SQLException {
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "SELECT p.relname, a.* FROM actions a, pg_class p WHERE id=? AND a.tableoid = p.oid");
        prep.setInt(1, id);
        try (ResultSet res = prep.executeQuery()) {
            if (res.next()) {
                return genAction(res);
            }
        }
        return null;
    }

    public static LinkedList<Action> getByCase(Case c) throws SQLException {
        LinkedList<Action> result = new LinkedList<Action>();
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "SELECT p.relname, a.id FROM actions a, pg_class p WHERE \"case\"=? AND a.tableoid = p.oid ORDER BY \"time\" ASC");
        prep.setInt(1, c.getId());
        try (ResultSet res = prep.executeQuery()) {
            while (res.next()) {
                result.add(genAction(res));
            }
        }
        return result;
    }

    private static Action genAction(ResultSet res) throws SQLException {
        PreparedStatement fetch = DatabaseConnection.getInstance().prepare(
                "SELECT a.*, extract(epoch from a.time)*1000 as epoch FROM "
                        + res.getString("relname") + " a WHERE id=?");
        fetch.setInt(1, res.getInt("id"));
        System.out.println(res.getString("relname"));

        switch (res.getString("relname")) {
        case "wizard_calls":
            try (ResultSet spec = fetch.executeQuery()) {
                if (spec.next()) {
                    return new WizardCall(spec);
                }
            }
            break;
        case "comments":
            try (ResultSet spec = fetch.executeQuery()) {
                if (spec.next()) {
                    return new CommentAction(spec);
                }
            }
            break;
        case "proxy_calls":
            try (ResultSet spec = fetch.executeQuery()) {
                if (spec.next()) {
                    return new ProxyCall(spec);
                }
            }
            break;
        default:
            Log.getLog().warn("Unknown action", res.getString("relname"));
            break;
        }
        return null;
    }

    public Action(ResultSet res) throws SQLException {
        this.id = res.getInt("id");
        this.caseId = res.getInt("case");
        this.date = new Date(res.getLong("epoch"));
        URL resource = getClass().getResource(
                getClass().getSimpleName() + ".templ");
        if (resource != null) {
            defaultTemplate = new Template(resource);
        }
    }

    public Date getTime() {
        return date;
    }

    public abstract Outputable output(Map<String, Object> vars, Supporter user)
            throws SQLException;

    protected Template getDefaultTemplate() {
        return defaultTemplate;
    }

    public int getId() {
        return id;
    }

    public int getCaseId() {
        return caseId;
    }

}
