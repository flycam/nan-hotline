package me.streib.janis.nanhotline.web.pages;

import me.streib.janis.nanhotline.web.dbobjects.Case;
import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.Template;

import javax.servlet.http.HttpServletRequest;
import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.Map;

/**
 * @author Anton Schirg
 */
public class CaseForm extends Form {
    static Template t;
    static {
        t = new Template(LoginForm.class.getResource("caseform.templ"));
    }

    private Case caze;

    public CaseForm(HttpServletRequest hsr, Case caze) {
        super(hsr);
        this.caze = caze;
    }

    @Override
    public boolean submit(PrintWriter out, HttpServletRequest req) {
        caze.setTitle(req.getParameter("title"));
        caze.setDescription(req.getParameter("description"));
        try {
            return caze.update();
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    @Override
    protected void outputContent(PrintWriter out, Map<String, Object> vars) {
        t.output(out, vars);
    }
}
