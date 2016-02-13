package me.streib.janis.nanhotline.web.pages;

import java.io.IOException;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.Map;
import java.util.regex.Matcher;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.dbobjects.Action;
import me.streib.janis.nanhotline.web.dbobjects.Case;
import me.streib.janis.nanhotline.web.dbobjects.Status;
import me.streib.janis.nanhotline.web.dbobjects.Supporter;

import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.IterableDataset;

public class CaseInspect extends Page {

    public CaseInspect() {
        super("Case");
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars, Matcher match) throws IOException,
            SQLException {
        String pathInfo = req.getPathInfo();
        int caseId = Integer.parseInt(match.group("id"));
        String action = match.group("action");
        if (action != null && !action.equals("")) {
            if (action.equals("assign")) {
                Case caze = Case.getCaseById(caseId);
                if (!caze.assign(getUser(req))) {
                    vars.put("error_message", "Could not assign case to user");
                } else {
                    resp.sendRedirect("/case/" + caseId);
                    return;
                }
            } else {
                vars.put("error_message", "Unknown action");
            }
        }

        Case c = Case.getCaseById(caseId);
        if (c == null) {
            //Check if case was merged
            Integer mergedCaseId = Case.getMergedId(caseId);
            if (mergedCaseId != null) {
                vars.put("merged", true);
                vars.put("merged_id", mergedCaseId);
                vars.put("case_id", caseId);
                getDefaultTemplate().output(resp.getWriter(), vars);
                return;
            } else {
                resp.sendError(404);
                return;
            }
        }
        vars.put("caseform", new CaseForm(req, c));
        vars.put("case_id", c.getId());
        vars.put("open", c.getStatus() == Status.OPEN);
        vars.put("case_title", c.getTitle());
        final Supporter supp = c.getAssignedSupporter();
        if (supp != null) {
            vars.put("case_supporter", supp.getName());
        } else {
            vars.put("no_supporter_assigned", true);
        }
        vars.put("description", c.getDescription());

        final LinkedList<Supporter> availSupporters = Supporter
                .getAllSupporters();
        vars.put("available_supporters", new IterableDataset() {
            @Override
            public boolean next(Map<String, Object> vars) {
                if (availSupporters.isEmpty()) {
                    return false;
                }
                Supporter s = availSupporters.removeFirst();
                vars.put("available_supporter_id", s.getId());
                vars.put("available_supporter_name", s.getName());
                vars.put("available_supporter_active",
                        supp != null && s.getId() == supp.getId());
                return true;
            }
        });

        final Supporter user = Page.getUser(req);
        final LinkedList<Action> actions = Action.getByCase(c);
        vars.put("actions", new IterableDataset() {

            @Override
            public boolean next(Map<String, Object> vars) {
                if (actions.isEmpty()) {
                    return false;
                }
                Action a = actions.removeFirst();
                try {
                    vars.put("action", a.output(vars, user));
                } catch (SQLException e) {
                    e.printStackTrace();
                    return false;
                }
                return true;
            }
        });
        vars.put("commentForm", new CommentForm(req, c));
        vars.put("mergeform", new MergeForm(req, c));
        getDefaultTemplate().output(resp.getWriter(), vars);
    }

    @Override
    public void doPost(HttpServletRequest req, HttpServletResponse resp,
            Map<String, Object> vars, Matcher match) throws IOException,
            SQLException {
        if (req.getParameter("comment") != null) {
            Form m = Form.getForm(req, CommentForm.class);
            m.submit(resp.getWriter(), req);
        } else if (req.getParameter("tomerge") != null) {
            Form m = Form.getForm(req, MergeForm.class);
            if (m.submit(resp.getWriter(), req)) {
                resp.sendRedirect("/case/" + req.getParameter("tomerge"));
            }

        } else {
            CaseForm form = Form.getForm(req, CaseForm.class);
            if (!form.submit(resp.getWriter(), req)) {
                resp.getWriter().println("Could not save changes");
            }
        }
        doGet(req, resp, vars, match);
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
