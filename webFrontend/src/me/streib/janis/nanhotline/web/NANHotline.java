package me.streib.janis.nanhotline.web;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.pages.CaseInspect;
import me.streib.janis.nanhotline.web.pages.LoginPage;
import me.streib.janis.nanhotline.web.pages.MainPage;
import me.streib.janis.nanhotline.web.pages.Page;
import me.streib.janis.nanhotline.web.pages.PhonePage;
import me.streib.janis.nanhotline.web.pages.UserPage;

import org.cacert.gigi.output.template.Outputable;
import org.cacert.gigi.output.template.Template;
import org.json.JSONException;

public class NANHotline extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private Page mainPage = new MainPage();
    private Template mainTemplate;
    private HashMap<String, Page> mapping = new HashMap<String, Page>();
    private PageRouter pageRouter = new PageRouter();

    @Override
    public void init() throws ServletException {
        super.init();
        mainTemplate = new Template(
                NANHotline.class.getResource("NANHotline.templ"));
        pageRouter.addPage("^/?$", mainPage);
        pageRouter.addPage("^/login/?$", new LoginPage());
        pageRouter.addPage("^/case/([0-9]*)$", new CaseInspect());
        pageRouter.addPage("^/user/?$", new UserPage());
        pageRouter.addPage("^/telephone/(.*)$", new PhonePage());
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
        final PageRouter.Result routeResult = pageRouter.getPage(pathInfo);

        if (routeResult == null) {
            resp.sendError(404);
            return;
        }

        if (routeResult.page.needsLogin() && !Page.isLoggedIn(req)) {
            req.getSession().setAttribute("redirOrig", pathInfo);
            resp.sendRedirect("/login");
            return;
        }

        if (routeResult.page.needsTemplate()) {

            Outputable content = new Outputable() {

                @Override
                public void output(PrintWriter out, Map<String, Object> vars) {
                    try {
                        routeDo(routeResult.page, req, resp, vars,
                                routeResult.matcher, method);
                    } catch (IOException | SQLException e) {
                        e.printStackTrace();
                    }
                }
            };
            vars.put(routeResult.page.getName(), "");
            vars.put("content", content);
            vars.put("year", Calendar.getInstance().get(Calendar.YEAR));
            vars.put("title", routeResult.page.getName());
            vars.put("username", Page.getUser(req).getUsername());
            mainTemplate.output(resp.getWriter(), vars);
        } else {
            routeDo(routeResult.page, req, resp, vars, routeResult.matcher,
                    method);
        }
    }

    private void routeDo(Page p, HttpServletRequest req,
            HttpServletResponse resp, Map<String, Object> vars, Matcher match,
            Method method) throws IOException, SQLException {
        switch (method) {
        case GET:
            p.doGet(req, resp, vars, match);
            break;
        case POST:
            p.doPost(req, resp, vars, match);
            break;
        case PUT:
            p.doPut(req, resp, vars, match);
            break;
        case DELETE:
            p.doDelete(req, resp, vars, match);
            break;
        default:
            break;
        }
    }
}
