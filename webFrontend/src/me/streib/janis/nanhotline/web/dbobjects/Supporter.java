package me.streib.janis.nanhotline.web.dbobjects;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.LinkedList;

import me.streib.janis.nanhotline.web.DatabaseConnection;

public class Supporter {
    private static final HashMap<Integer, Supporter> CACHE = new HashMap<Integer, Supporter>();

    public static Supporter getSupporterById(int id) throws SQLException {
        if (CACHE.containsKey(id)) {
            return CACHE.get(id);
        }
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "SELECT * FROM supporters WHERE id=?");
        prep.setInt(1, id);
        ResultSet res = prep.executeQuery();
        if (!res.next()) {
            return null;
        }
        Supporter s = new Supporter(res);
        res.close();
        CACHE.put(id, s);
        return s;
    }

    public static Supporter isSupporter(String username, String password)
            throws SQLException, NoSuchAlgorithmException,
            UnsupportedEncodingException {
        PreparedStatement prep = DatabaseConnection.getInstance().prepare(
                "SELECT * FROM supporters WHERE username=? AND password=?");
        prep.setString(1, username);
        MessageDigest messageDigest = MessageDigest.getInstance("SHA-512");
        messageDigest.update(password.getBytes("UTF-8"));
        String byteArrayToHexString = byteArrayToHexString(messageDigest
                .digest());
        prep.setString(2, byteArrayToHexString);
        ResultSet res = prep.executeQuery();
        if (res.next()) {
            Supporter s = new Supporter(res);
            res.close();
            return s;
        }
        res.close();
        return null;
    }

    private String name;
    private int id;
    private String username;

    public Supporter(ResultSet res) throws SQLException {
        this.name = res.getString("name");
        this.username = res.getString("username");
        this.id = res.getInt("id");
    }

    private static String byteArrayToHexString(byte[] b) {
        String result = "";
        for (int i = 0; i < b.length; i++) {
            result += Integer.toString((b[i] & 0xff) + 0x100, 16).substring(1);
        }
        return result;
    }

    public String getName() {
        return name;
    }

    public String getUsername() {
        return username;
    }

    public LinkedList<Phone> getPhones() throws SQLException {
        PreparedStatement prep = DatabaseConnection.getInstance()
                .prepare("SELECT * FROM supporter_phones WHERE supporter=?");
        prep.setInt(1, id);
        ResultSet resSet = prep.executeQuery();
        LinkedList<Phone> res = new LinkedList<>();
        while(resSet.next()) {
            res.add(new Phone(resSet));
        }
        return res;
    }

    public LinkedList<Case> getCases() throws SQLException {
        PreparedStatement prep = DatabaseConnection
                .getInstance()
                .prepare(
                        "SELECT * FROM cases WHERE assigned_supporter=? AND status=?::case_status");
        prep.setInt(1, id);
        prep.setString(2, Status.OPEN.name().toLowerCase());
        ResultSet resSet = prep.executeQuery();
        LinkedList<Case> res = new LinkedList<Case>();
        while (resSet.next()) {
            res.add(new Case(resSet));
        }
        resSet.close();
        return res;

    }
}
