package me.streib.janis.nanhotline.web;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import me.streib.janis.nanhotline.web.pages.LoginPage;
import me.streib.janis.nanhotline.web.pages.MainPage;
import me.streib.janis.nanhotline.web.pages.Page;

import org.cacert.gigi.output.template.Outputable;
import org.cacert.gigi.output.template.Template;
import org.json.JSONException;

public class NANHotline extends HttpServlet {
	private static final long serialVersionUID = 1L;
	private Page mainPage = new MainPage();
	private Template mainTemplate;
	private HashMap<String, Page> mapping = new HashMap<String, Page>();

	@Override
	public void init() throws ServletException {
		super.init();
		mainTemplate = new Template(
				NANHotline.class.getResource("NANHotline.templ"));
		mapping.put("/login", new LoginPage());
	}

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp)
			throws ServletException, IOException {
		try {
			handleRequest(req, resp, false);
		} catch (JSONException | SQLException e) {
			e.printStackTrace();
		}
	}

	@Override
	protected void doPost(HttpServletRequest req, HttpServletResponse resp)
			throws ServletException, IOException {
		try {
			handleRequest(req, resp, true);
		} catch (JSONException | SQLException e) {
			e.printStackTrace();
		}
	}

	private void handleRequest(final HttpServletRequest req,
			final HttpServletResponse resp, final boolean post)
			throws IOException, JSONException, SQLException {
		final String pathInfo = req.getPathInfo();
		resp.setContentType("text/html; charset=utf-8");
		if (NANHotlineConfiguration.getInstance().isHSTSEnabled()) {
			resp.setHeader("Strict-Transport-Security", "max-age=" + 60 * 60
					* 24 * 366 + "; preload");
		}
		HashMap<String, Object> vars = new HashMap<String, Object>();
		final Page p;
		if (pathInfo == null || pathInfo == "/") {
			p = mainPage;
		} else {
			p = mapping.get(pathInfo);
			if (p == null) {
				resp.sendError(404);
				return;
			}
		}
		if (p.needsLogin() && !Page.isLoggedIn(req)) {
			req.getSession().setAttribute("redirOrig", pathInfo);
			resp.sendRedirect("/login");
			return;
		}
		if (p.needsTemplate()) {

			Outputable content = new Outputable() {

				@Override
				public void output(PrintWriter out, Map<String, Object> vars) {
					try {
						if (post) {
							p.doPost(req, resp, vars);
						} else {
							p.doGet(req, resp, vars);
						}
					} catch (IOException e) {
						e.printStackTrace();
					} catch (JSONException e) {
						e.printStackTrace();
					} catch (SQLException e) {
						e.printStackTrace();
					}
				}
			};
			vars.put(p.getName(), "");
			vars.put("content", content);
			vars.put("year", Calendar.getInstance().get(Calendar.YEAR));
			vars.put("title", p.getName());
			mainTemplate.output(resp.getWriter(), vars);
		} else if (post) {
			p.doPost(req, resp, vars);
		} else {
			p.doGet(req, resp, vars);
		}
	}
}
