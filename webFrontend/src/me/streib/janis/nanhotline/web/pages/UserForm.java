package me.streib.janis.nanhotline.web.pages;

import me.streib.janis.nanhotline.web.dbobjects.Supporter;
import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.Template;

import javax.servlet.http.HttpServletRequest;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.security.NoSuchAlgorithmException;
import java.sql.SQLException;
import java.util.Map;

/**
 * @author Anton Schirg
 */
public class UserForm extends Form {
    static Template t;
    static {
        t = new Template(LoginForm.class.getResource("UserForm.templ"));
    }

    public UserForm(HttpServletRequest hsr) {
        super(hsr);
    }

    @Override
    public boolean submit(PrintWriter out, HttpServletRequest req) {
        Supporter supporter = Page.getUser(req);
        supporter.setName(req.getParameter("fullname"));
        supporter.setUsername(req.getParameter("username"));
        try {
            supporter.update();
        } catch (SQLException e) {
            System.out.println(e);
            return false;
        }
        String oldpass = req.getParameter("oldpass");
        String newpass = req.getParameter("newpass");
        String confirm = req.getParameter("newpassconf");
        if (!newpass.equals("")) {
            if (!newpass.equals(confirm)) {
                return false;
            }
            try {
                return supporter.updatePassword(oldpass, newpass);
            } catch (SQLException | UnsupportedEncodingException | NoSuchAlgorithmException e) {
                e.printStackTrace();
                return false;
            }
        }
        return true;
    }

    @Override
    protected void outputContent(PrintWriter out, Map<String, Object> vars) {
        t.output(out, vars);
    }
}
