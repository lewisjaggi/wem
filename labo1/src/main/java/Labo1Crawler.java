import java.io.IOException;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;

import org.apache.http.Header;

import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.common.SolrInputDocument;

public class Labo1Crawler extends WebCrawler {

    private static final String  CORE_NAME1 = "wemlabo1";
    private static final String  CORE_NAME2 = "wemlabo2";
    private static final Pattern IMAGE_EXTENSIONS = Pattern.compile(".*\\.(bmp|gif|jpg|png)$");

    private AtomicInteger numSeenImages;
    final SolrClient client = getSolrClient();
    /**
     * Creates a new crawler instance.
     *
     * @param numSeenImages This is just an example to demonstrate how you can pass objects to crawlers. In this
     * example, we pass an AtomicInteger to all crawlers and they increment it whenever they see a url which points
     * to an image.
     */
    public Labo1Crawler(AtomicInteger numSeenImages) {
        this.numSeenImages = numSeenImages;
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
        return href.startsWith("https://www.ics.uci.edu/");
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

        logger.debug("DocId: {}", docId);
        logger.info("URL: {}", url);
        logger.debug("Domain: '{}'", domain);
        logger.debug("Sub-domain: '{}'", subDomain);
        logger.debug("Path: '{}'", path);
        logger.debug("Parent page: {}", parentUrl);
        logger.debug("Anchor text: {}", anchor);

        if (page.getParseData() instanceof HtmlParseData) {
            HtmlParseData htmlParseData = (HtmlParseData) page.getParseData();
            String text = htmlParseData.getText();
            String html = htmlParseData.getHtml();
            Set<WebURL> links = htmlParseData.getOutgoingUrls();

            indexing1(docId, url, domain, subDomain, path, parentUrl, anchor, text, html, links);
            indexing2(docId, url, domain, subDomain, path, parentUrl, anchor, text, html, links);

            logger.debug("Text length: {}", text.length());
            logger.debug("Html length: {}", html.length());
            logger.debug("Number of outgoing links: {}", links.size());
        }

        Header[] responseHeaders = page.getFetchResponseHeaders();
        if (responseHeaders != null) {
            logger.debug("Response headers:");
            for (Header header : responseHeaders) {
                logger.debug("\t{}: {}", header.getName(), header.getValue());
            }
        }

        logger.debug("=============");
    }

    public HttpSolrClient getSolrClient() {
        final String solrUrl = "http://localhost:8983/solr";
        return new HttpSolrClient.Builder(solrUrl)
                .withConnectionTimeout(10000)
                .withSocketTimeout(60000)
                .build();
    }

    public void indexing1(int docId, String url, String domain, String subDomain, String path, String parentUrl, String anchor, String text, String html, Set<WebURL> links) {
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

        try {
            client.add(CORE_NAME2, doc);
            // Indexed documents must be committed
            client.commit(CORE_NAME2);
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

        try {
            client.add(CORE_NAME2, doc);
            // Indexed documents must be committed
            client.commit(CORE_NAME2);
        } catch (SolrServerException | IOException e) {
            e.printStackTrace();
        }
    }
}
