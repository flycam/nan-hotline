package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.cacert.gigi.output.template.Form;

public class LoginPage extends Page {

    public LoginPage() {
        super("Login");
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars) throws IOException {
        vars.put("loginform", new LoginForm(req));
        getDefaultTemplate().output(resp.getWriter(), vars);
    }

    @Override
    public void doPost(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars) throws IOException, SQLException {
        LoginForm lg = Form.getForm(req, LoginForm.class);
        if (!lg.submit(resp.getWriter(), req)) {
            resp.getWriter().println("Invalid Login");
            doGet(req, resp, vars);
        } else {
            String redir = (String) req.getSession().getAttribute("redirOrig");
            if (redir == null) {
                redir = "/";
            } else {
                req.getSession().setAttribute("redirOrig", null);
            }
            resp.sendRedirect(redir);
        }
    }

    @Override
    public boolean needsLogin() {
        return false;
    }

    @Override
    public boolean needsTemplate() {
        return true;
    }

}
