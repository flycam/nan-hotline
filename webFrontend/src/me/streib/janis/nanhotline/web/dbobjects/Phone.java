package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import me.streib.janis.nanhotline.web.DatabaseConnection;

public class Phone {
    private int id, supporter;
    private String sipUri;

    public static Phone getById(int id) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "SELECT * FROM supporter_phones WHERE id=?");
        prep.setInt(1, id);
        try (ResultSet res = prep.executeQuery()) {
            if (res.next()) {
                return new Phone(res);
            }
        }
        return null;
    }

    public Phone(ResultSet res) throws SQLException {
        id = res.getInt("id");
        sipUri = res.getString("sip_uri");
        supporter = res.getInt("supporter");
    }

    public Phone(String sipUri, Supporter supporter) throws SQLException {
        this.sipUri = sipUri;
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "INSERT INTO supporter_phones (sip_uri, supporter) VALUES (?, ?)");
        prep.setString(1, sipUri);
        prep.setInt(2, supporter.getId());
        prep.execute();
        prep.getGeneratedKeys().next();
        this.id = prep.getGeneratedKeys().getInt("id");
    }

    public static void deleteById(int id, int supporter_id) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "DELETE FROM supporter_phones WHERE id=? AND supporter=?");
        prep.setInt(1, id);
        prep.setInt(2, supporter_id);
        prep.execute();
    }

    public int getId() {
        return id;
    }

    public String getSipUri() {
        return sipUri;
    }

    public int getSupporter() {
        return supporter;
    }
}
