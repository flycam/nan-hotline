package me.streib.janis.nanhotline.web.pages;

import me.streib.janis.nanhotline.web.dbobjects.Phone;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Map;

/**
 * @author Anton Schirg
 */
public class PhonePage extends Page {
    public PhonePage() {
        super("Telephone");
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp, Map<String, Object> vars) throws IOException, SQLException {

    }

    @Override
    public void doPost(HttpServletRequest req, HttpServletResponse resp, Map<String, Object> vars) throws IOException, SQLException {
        String pathInfo = req.getPathInfo();
        int phoneId = Integer.parseInt(pathInfo.substring(
                pathInfo.lastIndexOf('/') + 1, pathInfo.length()));
        if (req.getParameter("delete").equals("true")) {
            Phone.deleteById(phoneId, getUser(req).getId());
            resp.sendRedirect("/user");
            return;
        }
    }

    @Override
    public boolean needsLogin() {
        return true;
    }

    @Override
    public boolean needsTemplate() {
        return true;
    }
}
