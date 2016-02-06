package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.net.URL;
import java.sql.SQLException;
import java.util.Map;
import java.util.regex.Matcher;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.dbobjects.Supporter;

import org.cacert.gigi.output.template.Template;

public abstract class Page {
    private Template defaultTemplate;
    private String name;

    public Page(String name) {
        this.name = name;
        if (needsTemplate()) {
            URL resource = getClass().getResource(
                    getClass().getSimpleName() + ".templ");
            if (resource != null) {
                defaultTemplate = new Template(resource);
            }
        }
    }

    /**
     * By default, {@link #doGet()} is called.
     */
    public void doPost(HttpServletRequest req, HttpServletResponse resp,
                       Map<String, Object> vars, Matcher match) throws IOException, SQLException {
        doGet(req, resp, vars, match);
    }

    public void doPut(HttpServletRequest req, HttpServletResponse resp,
                      Map<String, Object> vars, Matcher match) throws IOException, SQLException {
        doGet(req, resp, vars, match);
    }

    public void doDelete(HttpServletRequest req, HttpServletResponse resp,
                         Map<String, Object> vars, Matcher match) throws IOException, SQLException {
        doGet(req, resp, vars, match);
    }

    public abstract void doGet(HttpServletRequest req,
                               HttpServletResponse resp, Map<String, Object> vars, Matcher match)
            throws IOException, SQLException;

    public String getName() {
        return name;
    }

    public Template getDefaultTemplate() {
        return defaultTemplate;
    }

    public abstract boolean needsLogin();

    public abstract boolean needsTemplate();

    public static boolean isLoggedIn(HttpServletRequest req) {
        return req.getSession().getAttribute("user") != null;
    }

    public static Supporter getUser(HttpServletRequest req) {
        return (Supporter) req.getSession().getAttribute("user");
    }
}
