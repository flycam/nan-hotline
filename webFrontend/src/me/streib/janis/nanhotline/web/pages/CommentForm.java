package me.streib.janis.nanhotline.web.pages;

import java.io.PrintWriter;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import me.streib.janis.nanhotline.web.DatabaseConnection;
import me.streib.janis.nanhotline.web.dbobjects.Case;

import org.cacert.gigi.output.template.Form;
import org.cacert.gigi.output.template.Template;

public class CommentForm extends Form {
    static Template t;
    static {
        t = new Template(LoginForm.class.getResource("commentform.templ"));
    }
    private Case c;

    public CommentForm(HttpServletRequest hsr, Case c) {
        super(hsr);
        this.c = c;
    }

    @Override
    public boolean submit(PrintWriter out, HttpServletRequest req) {
        String comment = req.getParameter("comment");
        if (comment == null || comment.trim().isEmpty()) {
            return false;
        }
        PreparedStatement prep;
        try {
            prep = DatabaseConnection
                    .getInstance()
                    .prepare(
                            "INSERT INTO comments (time, supporter, \"case\", comment) VALUES(NOW(), ?, ?, ?)");

            prep.setInt(1, Page.getUser(req).getId());
            prep.setInt(2, c.getId());
            prep.setString(3, comment);
            prep.execute();
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    @Override
    protected void outputContent(PrintWriter out, Map<String, Object> vars) {
        t.output(out, vars);
    }

}
