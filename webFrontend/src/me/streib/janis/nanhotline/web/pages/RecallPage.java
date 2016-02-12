package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.SQLException;
import java.util.Map;
import java.util.regex.Matcher;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.dbobjects.Action;
import me.streib.janis.nanhotline.web.dbobjects.WizardCall;

public class RecallPage extends Page {

    public RecallPage() {
        super("Recall");
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars, Matcher match) throws IOException,
            SQLException {
        WizardCall a = (WizardCall) Action.getById(Integer.parseInt(match
                .group("id")));
        HttpURLConnection control = (HttpURLConnection) new URL(
                "http://localhost:9000/proxy").openConnection();
        control.setRequestMethod("POST");
        control.setDoOutput(true);
        OutputStream o = control.getOutputStream();
        o.write((a.getCaseId() + "&"
                + Integer.parseInt(req.getParameter("phone")) + "&" + a
                .getSupporteeSIPURI()).getBytes());
        o.flush();
        System.out.println(control.getResponseCode());
        resp.sendRedirect("/case/" + a.getCaseId());
    }

    @Override
    public boolean needsLogin() {
        return true;
    }

    @Override
    public boolean needsTemplate() {
        return false;
    }

}
