package me.streib.janis.nanhotline.web.dbobjects;

import me.streib.janis.nanhotline.web.DatabaseConnection;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class Phone {
    private int id;
    private String sipUri;

    public Phone(ResultSet res) throws SQLException {
        id = res.getInt("id");
        sipUri = res.getString("sip_uri");
    }

    public static void deleteById(int id, int supporter_id) throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "DELETE FROM supporter_phones WHERE id=? AND supporter=?"
        );
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
}
