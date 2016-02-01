package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class MainPage extends Page {

    public MainPage() {
        super("Dashboard");
    }

    @Override
    public boolean needsTemplate() {
        return true;
    }

    @Override
    public boolean needsLogin() {
        return true;
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars) throws IOException {
        getDefaultTemplate().output(resp.getWriter(), vars);
    }

}
