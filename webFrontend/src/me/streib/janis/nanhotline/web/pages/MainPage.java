package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.dbobjects.Case;

import org.cacert.gigi.output.template.IterableDataset;

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
            Map<String, Object> vars) throws IOException, SQLException {
        vars.put("fullname", getUser(req).getName());
        final LinkedList<Case> unassignedCases = Case.getUnassignedCases();
        vars.put("unassigned_cases", new IterableDataset() {

            @Override
            public boolean next(Map<String, Object> vars) {
                if (unassignedCases.isEmpty()) {
                    return false;
                }
                Case c = unassignedCases.removeFirst();
                vars.put("id", c.getId());
                vars.put("title", c.getTitle());
                vars.put("status", c.getStatus());
                return true;
            }
        });
        final LinkedList<Case> myCases = getUser(req).getCases();
        vars.put("my_cases", new IterableDataset() {

            @Override
            public boolean next(Map<String, Object> vars) {
                if (myCases.isEmpty()) {
                    return false;
                }
                Case c = myCases.removeFirst();
                vars.put("id", c.getId());
                vars.put("title", c.getTitle());
                vars.put("status", c.getStatus());
                return true;
            }
        });
        getDefaultTemplate().output(resp.getWriter(), vars);
    }
}
