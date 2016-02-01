package me.streib.janis.nanhotline.web.dbobjects;

import java.sql.ResultSet;
import java.sql.SQLException;

public class Phone {
    private String sipUri;
    private Supporter supp;

    public Phone(ResultSet res) throws SQLException {
        sipUri = res.getString("sip_uri");

    }

}
