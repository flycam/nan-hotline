package me.streib.janis.nanhotline.web.pages;

import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.security.NoSuchAlgorithmException;
import java.sql.SQLException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import me.streib.janis.nanhotline.web.dbobjects.Supporter;

import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.Template;

public class LoginForm extends Form {
    static Template t;
    static {
        t = new Template(LoginForm.class.getResource("loginform.templ"));
    }

    public LoginForm(HttpServletRequest hsr) {
        super(hsr);
    }

    @Override
    public boolean submit(PrintWriter out, HttpServletRequest req) {
        try {
            Supporter supporter = Supporter.isSupporter(
                    req.getParameter("user"), req.getParameter("pw"));
            if (supporter != null) {
                req.getSession().setAttribute("user", supporter);
                return true;
            }
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (SQLException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return false;
    }

    @Override
    protected void outputContent(PrintWriter out, Map<String, Object> vars) {
        t.output(out, vars);

    }
}
