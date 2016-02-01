package me.streib.janis.nanhotline.web;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.sql.SQLException;
import java.util.Properties;

public class NANHotlineConfiguration {
    private Properties p;
    private static NANHotlineConfiguration instance;

    protected NANHotlineConfiguration(InputStream in) throws IOException,
            SQLException {
        this.p = new Properties();
        p.load(in);
        instance = this;
    }

    public int getPort() {
        return Integer.parseInt(p.getProperty("nan.port"));
    }

    public String getHostName() {
        return p.getProperty("nan.name");
    }

    protected String getDB() {
        return p.getProperty("nan.db");
    }

    protected String getDBUser() {
        return p.getProperty("nan.db.user");
    }

    protected String getDBPW() {
        return p.getProperty("nan.db.pw");
    }

    protected String getJDBCDriver() {
        return p.getProperty("nan.db.driver");
    }

    public static NANHotlineConfiguration getInstance() {
        return instance;
    }

    private void store() {
        File f = new File("conf/");
        if (!f.exists()) {
            f.mkdir();
        }
        f = new File("conf/nanhotline.properties");
        try {
            p.store(new FileOutputStream(f), "");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    public boolean isHSTSEnabled() {
        return Boolean.getBoolean(p.getProperty("nan.hsts", "true"));
    }
}
