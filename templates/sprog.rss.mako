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
	<atom:link href="https://almoturg.com/sprog${"_no_context" if not show_parents else ""}.rss" rel="self" type="application/rss+xml" />
	<link>https://almoturg.com/sprog/</link>
	<description>Reddit poems by /u/Poem_for_your_sprog</description>
	<lastBuildDate>${build_date}</lastBuildDate>
	<language>en</language>
	<sy:updatePeriod>hourly</sy:updatePeriod>
	<sy:updateFrequency>6</sy:updateFrequency>
    % for poem in poems:
        <item>
		<title>${title_snippet(poem.orig_content)}</title>
		<link>${poem.link}</link>
		<pubDate>${format_timestamp(poem.datetime)}</pubDate>
		<dc:creator><![CDATA[/u/Poem_for_your_sprog]]></dc:creator>

		<guid isPermaLink="true">${poem.link}</guid>
        <content:encoded><![CDATA[
            % if show_parents:
                ${poem.submission_title}

                % if poem.submission_content:
                    <blockquote>${to_html(poem.submission_content)}</blockquote>
                % endif

                ${format_username(poem.submission_user)}
                % for parent_comment in poem.parents:
                    <blockquote>${to_html(parent_comment["orig_body"])}</blockquote>

                    ${format_username(parent_comment["author"])}
                % endfor
            % endif
            <blockquote>
                ${to_html(poem.orig_content)}
            </blockquote>
            &mdash; /u/Poem_for_your_sprog
            ]]></content:encoded>
        </item>
    % endfor

	</channel>
</rss>