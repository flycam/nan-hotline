package me.streib.janis.nanhotline.web.pages;

import me.streib.janis.nanhotline.web.dbobjects.Phone;
import me.streib.janis.nanhotline.web.dbobjects.Supporter;
import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.IterableDataset;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.Map;
import java.util.regex.Matcher;

/**
 * @author Anton Schirg
 */
public class UserPage extends Page {
    public UserPage() {
        super("Profile");
    }

    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp, Map<String, Object> vars, Matcher match) throws IOException, SQLException {
        vars.put("userform", new UserForm(req));
        Supporter user = getUser(req);
        vars.put("username", user.getUsername());
        vars.put("fullname", user.getName());

        final LinkedList<Phone> phones = user.getPhones();
        vars.put("telephones", new IterableDataset() {

            @Override
            public boolean next(Map<String, Object> vars) {
                if (phones.isEmpty()) {
                    return false;
                }
                Phone p = phones.removeFirst();
                vars.put("id", p.getId());
                vars.put("sip_uri", p.getSipUri());
                return true;
            }
        });
        getDefaultTemplate().output(resp.getWriter(), vars);
    }

    @Override
    public void doPost(HttpServletRequest req, HttpServletResponse resp, Map<String, Object> vars, Matcher match) throws IOException, SQLException {
        UserForm form = Form.getForm(req, UserForm.class);
        if (!form.submit(resp.getWriter(), req)) {
            resp.getWriter().println("Could not save changes");
            doGet(req, resp, vars, match);
        } else {
            resp.sendRedirect("/user");
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
