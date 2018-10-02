<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:atom="http://www.w3.org/2005/Atom"
	xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
	xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
	>

<channel>
	<title>Poem for your Sprog</title>
	<atom:link href="https://almoturg.com/sprog.rss" rel="self" type="application/rss+xml" />
	<link>https://almoturg.com/sprog/</link>
	<description>Reddit poems by /u/Poem_for_your_sprog</description>
	<lastBuildDate>${build_date}</lastBuildDate>
	<language>en</language>
	<sy:updatePeriod>hourly</sy:updatePeriod>
	<sy:updateFrequency>6</sy:updateFrequency>
    % for poem in poems:
        <item>
		<title>${converter(title_snippet(poem.orig_content))}</title>
		<link>${poem.link}</link>
		<pubDate>${poem.datetime.isoformat()}</pubDate>
		<dc:creator><![CDATA[/u/Poem_for_your_sprog]]></dc:creator>

		<guid isPermaLink="true">${poem.link}</guid>
        <content:encoded><![CDATA[
            % if show_parents:
                ${poem.submission_title}
                % if poem.submission_content:
                    <blockquote>${converter(poem.submission_content)}</blockquote>
                % endif
                &mdash; ${"/u/" if poem.submission_user != "deleted" else ""}${converter(poem.submission_user)}
                % for parent_comment in poem.parents:
                    <blockquote>${converter(parent_comment["orig_body"])}</blockquote>
                    &mdash; ${"/u/" if parent_comment["author"] != "deleted" else ""}${converter(parent_comment["author"])}
                % endfor
            % endif
            <blockquote>
                ${converter(poem.orig_content)}
            </blockquote>
            &mdash; /u/Poem_for_your_sprog
            ]]></content:encoded>
        </item>
    % endfor

	</channel>
</rss>