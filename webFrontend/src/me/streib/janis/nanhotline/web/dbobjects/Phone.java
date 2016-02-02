package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;

public class Phone {
    private int id;
    private String sipUri;

    public Phone(ResultSet res) throws SQLException {
        id = res.getInt("id");
        sipUri = res.getString("sip_uri");
    }

    public int getId() {
        return id;
    }

    public String getSipUri() {
        return sipUri;
    }
}
