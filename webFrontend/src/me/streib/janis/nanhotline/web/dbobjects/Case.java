package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;

import me.streib.janis.nanhotline.web.DatabaseConnection;

public class Case {

    private int id;
    private String title, description;
    private Supporter assignedSupporter;
    private Status status;

    public static Case getCaseById(int id) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "SELECT * FROM cases WHERE id=?");
        prep.setInt(1, id);
        ResultSet resSet = prep.executeQuery();
        if (resSet.next()) {
            Case c = new Case(resSet);
            resSet.close();
            return c;
        }
        return null;
    }

    public static LinkedList<Case> getUnassignedCases() throws SQLException {
        LinkedList<Case> res = new LinkedList<Case>();
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "SELECT * FROM cases WHERE assigned_supporter ISNULL AND status=?::case_status ORDER BY id ASC");
        prep.setObject(1, Status.OPEN.name().toLowerCase());
        ResultSet resSet = prep.executeQuery();
        while (resSet.next()) {
            res.add(new Case(resSet));
        }
        resSet.close();
        return res;
    }

    public Case(ResultSet res) throws SQLException {
        this.id = res.getInt("id");
        this.title = res.getString("title");
        this.description = res.getString("description");
        this.assignedSupporter = Supporter.getSupporterById(res
                .getInt("assigned_supporter"));
        this.status = Status.valueOf(res.getString("status").toUpperCase());

    }

    public Supporter getAssignedSupporter() {
        return assignedSupporter;
    }

    public String getDescription() {
        return description;
    }

    public int getId() {
        return id;
    }

    public Status getStatus() {
        return status;
    }

    public String getTitle() {
        return title;
    }
}
