package me.streib.janis.nanhotline.web;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.pages.CaseInspect;
import me.streib.janis.nanhotline.web.pages.LoginPage;
import me.streib.janis.nanhotline.web.pages.MainPage;
import me.streib.janis.nanhotline.web.pages.Page;
import me.streib.janis.nanhotline.web.pages.UserPage;

import org.cacert.gigi.output.template.Outputable;
import org.cacert.gigi.output.template.Template;
import org.json.JSONException;

public class NANHotline extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private Page mainPage = new MainPage();
    private Template mainTemplate;
    private HashMap<String, Page> mapping = new HashMap<String, Page>();

    @Override
    public void init() throws ServletException {
        super.init();
        mainTemplate = new Template(
                NANHotline.class.getResource("NANHotline.templ"));
        mapping.put("/login", new LoginPage());
        mapping.put("/case/*", new CaseInspect());
        mapping.put("/user", new UserPage());
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        try {
            handleRequest(req, resp, Method.GET);
        } catch (JSONException | SQLException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void doDelete(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        try {
            handleRequest(req, resp, Method.DELETE);
        } catch (JSONException | SQLException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void doPut(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        try {
            handleRequest(req, resp, Method.PUT);
        } catch (JSONException | SQLException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        try {
            handleRequest(req, resp, Method.POST);
        } catch (JSONException | SQLException e) {
            e.printStackTrace();
        }
    }

    private void handleRequest(final HttpServletRequest req,
            final HttpServletResponse resp, final Method method)
            throws IOException, JSONException, SQLException {
        final String pathInfo = req.getPathInfo();
        resp.setContentType("text/html; charset=utf-8");
        if (NANHotlineConfiguration.getInstance().isHSTSEnabled()) {
            resp.setHeader("Strict-Transport-Security", "max-age=" + 60 * 60
                    * 24 * 366 + "; preload");
        }
        HashMap<String, Object> vars = new HashMap<String, Object>();
        Page tmpp = null;
        if (pathInfo == null || pathInfo == "/") {
            tmpp = mainPage;
        } else {
            tmpp = mapping.get(pathInfo);
            if (tmpp == null) {
                tmpp = mapping.get(pathInfo + "/*");
                if (tmpp == null) {
                    tmpp = mapping.get(pathInfo.substring(0,
                            pathInfo.lastIndexOf('/'))
                            + "/*");
                    if (tmpp == null) {
                        resp.sendError(404);
                        return;
                    }
                }

            }
        }
        if (tmpp.needsLogin() && !Page.isLoggedIn(req)) {
            req.getSession().setAttribute("redirOrig", pathInfo);
            resp.sendRedirect("/login");
            return;
        }
        final Page p = tmpp;
        if (p.needsTemplate()) {

            Outputable content = new Outputable() {

                @Override
                public void output(PrintWriter out, Map<String, Object> vars) {
                    try {
                        routeDo(p, req, resp, vars, method);
                    } catch (IOException | SQLException e) {
                        e.printStackTrace();
                    }
                }
            };
            vars.put(p.getName(), "");
            vars.put("content", content);
            vars.put("year", Calendar.getInstance().get(Calendar.YEAR));
            vars.put("title", p.getName());
            mainTemplate.output(resp.getWriter(), vars);
        } else {
            routeDo(p, req, resp, vars, method);
        }
    }

    private void routeDo(Page p, HttpServletRequest req,
            HttpServletResponse resp, Map<String, Object> vars, Method method)
            throws IOException, SQLException {
        switch (method) {
        case GET:
            p.doGet(req, resp, vars);
            break;
        case POST:
            p.doPost(req, resp, vars);
            break;
        case PUT:
            p.doPut(req, resp, vars);
            break;
        case DELETE:
            p.doDelete(req, resp, vars);
            break;
        default:
            break;
        }
    }
}
