package me.streib.janis.nanhotline.web.pages;

import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import me.streib.janis.nanhotline.web.dbobjects.Case;

import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.Template;

public class MergeForm extends Form {
    static Template t;
    static {
        t = new Template(LoginForm.class.getResource("mergeform.templ"));
    }

    private Case caze;

    public MergeForm(HttpServletRequest hsr, Case c) {
        super(hsr);
        this.caze = c;
    }

    @Override
    public boolean submit(PrintWriter out, HttpServletRequest req) {
        try {
            return caze.merge(Integer.parseInt(req.getParameter("tomerge")));
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
