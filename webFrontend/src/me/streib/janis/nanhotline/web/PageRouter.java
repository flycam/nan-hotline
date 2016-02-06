package me.streib.janis.nanhotline.web;

import me.streib.janis.nanhotline.web.pages.Page;

import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PageRouter {
    private LinkedList<PageInfo> pages = new LinkedList<>();

    public void addPage(String pattern, Page page) {
        Pattern r = Pattern.compile(pattern);
        pages.add(new PageInfo(r, page));
    }

    public Result getPage(String url) {
        for (PageInfo info : pages) {
            Matcher m = info.pattern.matcher(url);
            if (m.matches()) {
                return new Result(info.page, m);
            }
        }
        return null;
    }

    private class PageInfo {
        Pattern pattern;
        Page page;

        public PageInfo(Pattern pattern, Page page) {
            this.pattern = pattern;
            this.page = page;
        }
    }

    class Result {
        Page page;
        Matcher matcher;

        private Result(Page page, Matcher matcher) {
            this.page = page;
            this.matcher = matcher;
        }
    }
}
