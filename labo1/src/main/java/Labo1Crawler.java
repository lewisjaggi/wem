import java.io.IOException;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;

import com.google.gson.Gson;
import org.apache.http.Header;

import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.apache.solr.common.SolrInputDocument;
import org.apache.solr.common.params.MapSolrParams;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;


public class Labo1Crawler extends WebCrawler {

    private static final String CORE_NAME1 = "wemlabo1";
    private static final String CORE_NAME2 = "wemlabo2";
    private static final Pattern IMAGE_EXTENSIONS = Pattern.compile(".*\\.(bmp|gif|jpg|png)$");

    private AtomicInteger numSeenImages;
    private final SolrClient client = getSolrClient();
    private final Gson gson = new Gson();

    /**
     * Creates a new crawler instance.
     *
     * @param numSeenImages This is just an example to demonstrate how you can pass objects to crawlers. In this
     *                      example, we pass an AtomicInteger to all crawlers and they increment it whenever they see a url which points
     *                      to an image.
     */
    public Labo1Crawler(AtomicInteger numSeenImages, Boolean clear) throws IOException, SolrServerException {

        this.numSeenImages = numSeenImages;
        if (clear) {
            this.clear();
        }
    }

    public Labo1Crawler(AtomicInteger numSeenImages) throws IOException, SolrServerException {

        this(numSeenImages, false);

    }

    /**
     * You should implement this function to specify whether the given url
     * should be crawled or not (based on your crawling logic).
     */
    @Override
    public boolean shouldVisit(Page referringPage, WebURL url) {
        String href = url.getURL().toLowerCase();
        // Ignore the url if it has an extension that matches our defined set of image extensions.
        if (IMAGE_EXTENSIONS.matcher(href).matches()) {
            numSeenImages.incrementAndGet();
            return false;
        }

        // Only accept the url if it is in the "www.ics.uci.edu" domain and protocol is "http".
        return href.startsWith("http://www.allocine.fr/film/");
    }

    /**
     * This function is called when a page is fetched and ready to be processed
     * by your program.
     */
    @Override
    public void visit(Page page) {

        int docId = page.getWebURL().getDocid();
        String url = page.getWebURL().getURL();
        String domain = page.getWebURL().getDomain();
        String path = page.getWebURL().getPath();
        String subDomain = page.getWebURL().getSubDomain();
        String parentUrl = page.getWebURL().getParentUrl();
        String anchor = page.getWebURL().getAnchor();

        if (page.getParseData() instanceof HtmlParseData) {
            HtmlParseData htmlParseData = (HtmlParseData) page.getParseData();
            String text = htmlParseData.getText();
            String html = htmlParseData.getHtml();
            Set<WebURL> links = htmlParseData.getOutgoingUrls();


            //indexing1(page);
            indexing2(docId, url, domain, subDomain, path, parentUrl, anchor, text, html, links);
        }
    }

    private HttpSolrClient getSolrClient() {
        final String solrUrl = "http://localhost:8983/solr/";
        return new HttpSolrClient.Builder(solrUrl)
                .withConnectionTimeout(10000)
                .withSocketTimeout(60000)
                .build();
    }


    public void indexing1(Page page) {
        final SolrInputDocument doc = new SolrInputDocument();
        doc.addField("page", page);

        try {
            client.add(CORE_NAME1, doc);
            // Indexed documents must be committed
            client.commit(CORE_NAME1);
        } catch (SolrServerException | IOException e) {
            e.printStackTrace();
        }
    }

    public void indexing2(int docId, String url, String domain, String subDomain, String path, String parentUrl, String anchor, String text, String html, Set<WebURL> links) {
        final SolrInputDocument doc = new SolrInputDocument();
        doc.addField("docId", docId);
        doc.addField("url", url);
        doc.addField("domain", domain);
        doc.addField("subDomain", subDomain);
        doc.addField("path", path);
        doc.addField("parentUrl", parentUrl);
        doc.addField("anchor", anchor);
        doc.addField("text", text);
        doc.addField("html", html);
        doc.addField("links", links);

        //get title
        Document jHtml = Jsoup.parse(html);
        Element title = jHtml.select("div.titlebar-title").first();
        doc.addField("title", title.text());

        //get notes
        Element htmlnotes = jHtml.getElementsByClass("rating-holder").first();
        HashMap<String, String> notes = new HashMap<>();

        for (Element htmlnote : htmlnotes.children()) {
            notes.put(htmlnote.getElementsByClass("rating-title").first().text(), htmlnote.getElementsByClass("stareval-note").first().text());
        }
        doc.addField("notes", gson.toJson(notes.toString()));

        //get date
        Element date = jHtml.getElementsByClass("date").first();
        doc.addField("date", date.text());

        //get real
        Elements real = jHtml.select("meta");
        for (Element e : real) {
            if (e.attr("property").equals("video:director")) {
               doc.addField("realisateur", e.attr("content"));
            }

        }

        //get actors
        List listActors = new ArrayList<String>();
        Elements actors = jHtml.getElementsByClass("meta-body-actor").first().children();
        for (Element e : actors) {
            if (!e.className().equals( "ligth")) {
               listActors.add(e.text());
            }

        }

        doc.addField("actors", gson.toJson(listActors.toString()));

        //get synopsis
        Element syn = jHtml.getElementsByClass("content-txt").first();
        doc.addField("synopsis", syn.text());


        try {
            client.add(CORE_NAME2, doc);
            // Indexed documents must be committed
            client.commit(CORE_NAME2);
        } catch (SolrServerException | IOException e) {
            e.printStackTrace();
        }
    }

    private void clear() throws IOException, SolrServerException {
        client.deleteByQuery(CORE_NAME1, "*");
        client.commit(CORE_NAME1);
        client.deleteByQuery(CORE_NAME2, "*");
        client.commit(CORE_NAME2);
    }

    public SolrDocumentList query(ArrayList<String> titles, ArrayList<String> realisateurs) {
        try {
            String lstTitles = "";
            for(String title: titles) {
                lstTitles += "title:" + title + " OR ";
            }
            String lstRealisateurs = "";
            for(String realisateur: realisateurs) {
                lstRealisateurs += "realisateur:" + realisateur + " OR ";
            }
            lstRealisateurs = lstRealisateurs.substring(0, lstRealisateurs.length() - 5);

            final Map<String, String> queryParamMap = new HashMap<String, String>();
            queryParamMap.put("q", lstTitles + lstRealisateurs);
            queryParamMap.put("fl", "id, title, realisateur, synopsis, score");
            queryParamMap.put("sort","score DESC");
            final QueryResponse response;
            MapSolrParams queryParams = new MapSolrParams(queryParamMap);

            response = client.query(CORE_NAME2, queryParams);

            return response.getResults();
        } catch (SolrServerException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }
}
