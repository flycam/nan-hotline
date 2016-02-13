package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
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

    public boolean assign(Supporter user) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "UPDATE cases SET assigned_supporter = ? WHERE id=?");
        if (user == null) {
            prep.setNull(1, Types.INTEGER);
        } else {
            prep.setInt(1, user.getId());
        }
        prep.setInt(2, id);
        int updateCount = prep.executeUpdate();
        if (updateCount == 0) {
            return false;
        }
        this.assignedSupporter = user;
        return true;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public boolean update() throws SQLException {
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "UPDATE cases SET (title, description, status) = (?, ?, ?::case_status) WHERE id=?");
        prep.setString(1, title);
        prep.setString(2, description);
        prep.setString(3, status.name().toLowerCase());
        prep.setInt(4, id);
        int updateCount = prep.executeUpdate();
        return updateCount != 0;
    }

    public boolean merge(int caseId) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "UPDATE actions SET \"case\"=? WHERE \"case\"=?");
        prep.setInt(1, caseId);
        prep.setInt(2, getId());
        prep.execute();

        prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "UPDATE cases SET title=? WHERE id=? AND (title ='') IS NOT FALSE");
        prep.setString(1, title);
        prep.setInt(2, caseId);
        prep.execute();

        prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "UPDATE cases SET assigned_supporter=? WHERE id=? AND assigned_supporter IS NULL");
        prep.setInt(1, assignedSupporter.getId());
        prep.setInt(2, caseId);
        prep.execute();

        prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "UPDATE cases SET description=? WHERE id=? AND (description ='') IS NOT FALSE");
        prep.setString(1, description);
        prep.setInt(2, caseId);
        prep.execute();

        prep = DatabaseConnection.getInstance().prepare(
                "DELETE FROM cases WHERE id=?");
        prep.setInt(1, getId());
        prep.execute();
        return true;
    }
}
