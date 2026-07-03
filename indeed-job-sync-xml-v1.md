Job Sync XML feed reference
Use an XML feed to define your jobs and how they appear on Indeed.

&nbsp;
legal notice
By using this API and its documentation and building an integration, you agree to the Additional API Terms and Guidelines.
Indeed does not support HTML entities in XML feeds. Use literal characters instead, such as < instead of &lt;. HTML entities can cause Indeed to reject the content or format it incorrectly.

Before you start, review Applicant tracking system | ATS integrations.

The Indeed XML feed contains the job information that appears on Indeed. When you maintain an XML feed, you control how jobs appear on Indeed. You can also add the Indeed Apply label to jobs.

When your customers create jobs in your system, your XML feed sends those listings directly to Indeed.

The XML feed
Create and maintain an XML document that defines your jobs. Indeed monitors the file for changes in one of these ways:

Crawling an XML URL
Crawling a client-hosted FTP site (SFTP is also supported)
Receiving the file directly on an Indeed FTP server (zipped files are recommended)
Include all jobs from your career page in the XML feed. Indeed does not accept incomplete XML feeds and does not support partial job opt-in. If your XML file does not include all jobs, Indeed might reject it or limit its visibility to job seekers.

Include in the XML all information that job seekers can see on your website. For example, if your job listings show salaries, include a data element such as <salary>. If salary information does not appear on your website, you do not need to include it for indexing.

Basic feed nodes
Basic feed nodes define general details for an XML feed, including the XML version and encoding, and ATS information (for ATS developers).

If Indeed requests modifications to your feed, make the corrections. Otherwise, Indeed might reject the feed loading request or stop loading feeds that are already active.

Basic feed nodes
Element	Description
<?xml ?>

Required

XML declaration.

Example:

<?xml version="1.0" encoding="utf-8"?>

<source>

Required

Root node for the XML feed document.

<publisher>

ATS developers only

Name of the ATS that published this job.

Example:

ATS Name

<publisherurl>

ATS developers only

URL of the ATS that published this job.

Example:

http://www.atssite.com/

<job>

Required

Job-specific metadata.

Define one <job> node for each job that appears on Indeed. Each <job> node defines job-specific metadata in Job feed elements.

Job feed elements
Job feed elements define job-specific metadata for a node.

Job feed elements
Element	Description
<title>

Required (except in Japan)

Title of the job. Exclude salary, employment type, location, descriptions, and headlines.

See also Misleading Content and Activities.

Example:

<![CDATA[Sales Executive]]>
<date>

Required

Date when you first published the job. Use ISO-8601 format.

If your site shows the publish date, the date must match the XML date.

Example:

<![CDATA[2014-12-19T22:49:39Z]]>
<referencenumber>

Required

Unique ID for this job instance.

Give jobs posted in multiple locations unique values. Do not change the value after you set it.

Example:

<![CDATA[unique123131]]>
<requisitionid>

Required

Requisition ID for the job (formerly external job ID).

Your system likely uses this value to track the original role and applicants.

The value might appear on your public career page.

Use the same value for each posting across feeds and locations. The value might not be unique.

Example:

<![CDATA[ab1212]]>
<apijobid>

Job ID.

Provide this element only when <apijobid> differs from <requisitionid>.

Indeed integrations such as Candidate Sync use this value to send candidate information to your system.

Example:

<![CDATA[ab1212]]>
<url>

Required

URL for this job listing on your site.

Use the job description page URL, not the application page.

Include source=Indeed to track clicks from Indeed.

Example:

<![CDATA[http://www.examplesite.com/viewjob.cfm?jobid=unique123131&source=Indeed]]>
<company>

Required

Parent organization hiring for the role.

For subsidiaries or franchises with multiple locations, use the same <sourcename> for all jobs.

Example:

<![CDATA[[ABC Hospital]]>
<sourcename>

ATS developers only

Required

Parent organization hiring for the role.

For subsidiaries or franchises with multiple locations, use the same <sourcename> for all jobs.

Example:

<![CDATA[ABC Medical Group]]>
<city>

Required

City where this job is located.

Example:

<![CDATA[Phoenix]]>
<state>

Required

State where this job is located.

Use postal abbreviations. Outside the US, use the matching province or region.

Example:

<![CDATA[AZ]]>
<country>

Required

Country where this job is located.

Example:

<![CDATA[US]]>
<postalcode>

Required if on the career site

Postal code where this job is located.

Example:

<![CDATA[85003]]>
<streetaddress>

Required if on the career site

Street address of the job's primary work location.

Include the street name and number.

Indeed uses the address for location-based search and display.

Example:

<![CDATA[1234 Sunny Lane
Phoenix, AZ 85003]]>

<email>

Required

Email address tied to the Indeed account for this client.

The Indeed Search Quality team uses this address to verify the business entity that posts the job.

Example:

<![CDATA[example@abccorp.com]]>
<description>

Required

Job description that job seekers see on Indeed. Match the content and order on your <url> page, including education and experience details.

Indeed might filter out buttons or link text that does not fit the Indeed context.

Include HTML formatting. For supported elements, see Formatting guidelines.

Example:

<![CDATA[<h2 id="job_description">Job Description:</h2><ul><li>Do you have 1–3 years of sales experience?</li></ul>]]>

<salary>

Required if on the career site

Salary offered for this job.

For best practices, see How to Display Pay Information in Job Postings.

If a job has no salary, leave the field blank in the XML for that job.

Indeed might also pull salary information directly from the job description, in addition to or instead of the value you set in <salary>.

If you do not enter the salary in the correct numerical format, Indeed might not display the salary or other pay data from this XML field. For the most predictable results, follow the salary best practices and provide the value in this XML field.

Examples:

<![CDATA[$50000 per year]]>
<![CDATA[$4000 - $5000 per month]]>
<![CDATA[年収500万円]]>
<![CDATA[月給40万円～50万円]]>
<education>

Required if on the career site

Education level required for this job.

Example:

<![CDATA[Bachelors]]
<jobtype>

Required if on the career site

Type of job: full-time or part-time.

Indeed might also pull this value directly from other job content that you provide.

Example:

<![CDATA[fulltime, parttime]]
<category>

Comma-delimited list of job categories that help job seekers refine their search.

Indeed strongly recommends that you include this field to manage jobs, to help clients sponsor jobs by category, or to surface extra information from the job details page.

For example, you can include facility or department information in this field.

Example:

<![CDATA[Category1, Category2, CategoryN]]>
<experience>

Required if on the career site

Experience required for this job.

Example:

<![CDATA[5+ years]]>
<expirationdate>

Required if on the career site

Date when active hiring for the role ends.

After this date, Indeed might remove the job from search results. Indeed interprets the date in the CST time zone by default.

Example:

<![CDATA[2021-11-08]]>
<tracking_url>

Note: This feature is not available in Japan.

Unique URL for the job. Indeed uses this URL to track clicks on the job and sends a GET request to this URL each time a user clicks the job.

Example:

<![CDATA[https://www.examplesite.com/trackjob1234]]>

<remotetype>

Type of remote work. Use one of these values:

Fully remote. The employee works remotely or from home. A fully remote job might not have a residency requirement narrower than nationwide because remote jobs appear nationwide.


Hybrid remote. The employee splits time between the office and remote work on a consistent basis.


COVID-19. The employee works remotely on a temporary basis because of COVID-19. The employee returns to the office part-time or full-time later on.


For more about remote jobs, see these sections in the How to post a remote job on Indeed article (Japanese article):

If your job appears on Indeed but is posted on your career site or ATS
XML file users
Indeed does not use this element to determine the location.

For text you can include in the job and for more about remote job postings, see XML feed FAQ.

Example:

<![CDATA[COVID-19]]>
<lastactivitydate>

Most recent timestamp of any action that your system took on this job.

Actions can include candidate review, job update, and so on.

Example:

<![CDATA[2014-12-19T22:49:39Z]]>
<billingId>

Identifier that clients use internally to identify their own business units.

Example:

abc123
<hide_from_indeed_search>

Controls whether the job post appears in Indeed search. Provide one of these reason codes:

CONFIDENTIAL_JOB: Confidential job postings that should not appear in Indeed search.

Example: An employer who discreetly replaces a role hides the posting from Indeed search and uses targeted channels (AutoSourcer, I2A, Smart Sourcing, or off-Indeed outreach) instead.

TALENT_POOL: Postings that build a candidate pool for future openings, not currently open roles. These postings should not appear in Indeed search.

Example: A company that plans to expand next quarter creates a talent pool posting to gather candidates before the positions open.

OPT_OUT: Rare or exceptional cases where you hide jobs from Indeed search for reasons that other codes do not cover.

Do not use this code for general opt-out or to circumvent policy.

Always discuss this code with your partner manager in advance.

Example:

<![CDATA[OPT_OUT]]>
XML feed example
This example XML feed defines one job:

<?xml version="1.0" encoding="utf-8"?>
<source>
  <!--publisher is applicable to ATS developers only-->
  <publisher>ATS Name</publisher>
  <!--publisherurl is applicable to ATS developers only-->
  <publisherurl>http://www.atssite.com</publisherurl>
  <job>
    <title>
      <![CDATA[Sales Executive]]>
    </title>
    <date>
      <![CDATA[2021-06-29T22:49:39Z]]>
    </date>
    <referencenumber>
      <![CDATA[unique123131]]>
    </referencenumber>
    <requisitionid>
      <![CDATA[ab1212]]>
    </requisitionid>
    <url>
      <![CDATA[http://www.examplesite.com/viewjob.cfm?jobid=unique123131&source=Indeed]]>
    </url>
    <company>
      <![CDATA[ABC Hospital]]>
    </company>
    <sourcename>
      <![CDATA[ABC Medical Group]]>
    </sourcename>
    <city>
      <![CDATA[Phoenix]]>
    </city>
    <state>
      <![CDATA[AZ]]>
    </state>
    <country>
      <![CDATA[US]]>
    </country>
    <postalcode>
      <![CDATA[85003]]>
    </postalcode>
    <streetaddress>
      <![CDATA[123 fake street Phoenix AZ, 85003]]>
    </streetaddress>
    <email>
      <![CDATA[example@abccorp.com]]>
    </email>
    <description>
      <![CDATA[Do you have 1-3 years of sales experience? Are you
            relentless at closing the deal? Are you ready for an exciting and
            high-speed career in sales? If so, we want to hear from you! [...]
            We provide competitive compensation, including stock options and a full
            benefit plan. As a fast-growing business, we offer excellent opportunities
            for exciting and challenging work. As our company continues to grow, you
            can expect unlimited career advancement! ]]>
    </description>
    <salary>
      <![CDATA[$50000 per year]]>
    </salary>
    <education>
      <![CDATA[Bachelors]]>
    </education>
    <jobtype>
      <![CDATA[fulltime, parttime]]>
    </jobtype>
    <category>
      <![CDATA[Category1, Category2, CategoryN]]>
    </category>
    <experience>
      <![CDATA[5+ years]]>
    </experience>
    <expirationdate>
      <![CDATA[2021-11-08]]>
    </expirationdate>
    <remotetype>
      <![CDATA[Fully remote]]>
    </remotetype>
    <indeed-apply-data>COVERED IN A LATER SECTION</indeed-apply-data>
  </job>
</source>
This XML feed renders this Indeed job listing:

Example of the job post rendered on Indeed
Example of the job post rendered on Indeed
Formatting guidelines
When you define job descriptions in the XML feed, wrap HTML formatting in CDATA tags. Use the same HTML formatting in CDATA tags that appears on your website.

Indeed normalizes and renders HTML in a standardized format for job seekers. It does not require strict HTML standards compliance.

HTML tags
Tag	Description
<b>	Bold text.
<h1> to <h6>

Header.

Text in header tags appears in consistent sizes on Indeed.

<br>	Single line break.
<p>	Paragraph. Indeed automatically inserts an empty line between paragraph tags.
<ul>	Unordered, or bulleted, list.
<li>	List item.
<strong>	Strong, or bold, text.
<em>	Emphasized, or italicized, text.
<table>

<thead>, <tbody>

<tr>

<th>, <td>

Simple table.
Computed-style nodes
Node	Description
<font style=\"font-weight:bold\">Some bold text</font>

Bold text.
<div><h2 style=\"display:inline\">Label: </h2>Text</div>

Inline text.

By default, <h2> is a block tag.

The <p> tag has positive top and bottom margins and padding by default. Do not override this.

About new element settings
Japan only.
You can configure these new elements in addition to existing elements (optional).

New element settings table
Element	Description
<timeshift>	
Work hours, working time, shifts, and similar information.

<subwayaccess>	
Transportation access information, such as "X minutes from ○○○ station".

<rawlocation>	
Detailed work location, such as street address and building.

<expdate>	
Listing end date.

<benefits>	
Benefits and welfare, such as "full transportation reimbursement".

<rawsalary>	
Detailed salary information.

<hires>	
Number of planned hires.

<keywords>	
Keyword list, such as "No experience OK" or "No overtime".


Indeed maintains a code table that maps each code to the text displayed in Indeed search results and on job detail pages. Specify the corresponding code in the feed to display the tag.


Contact your Indeed representative for the code table.

<imageUrls>	
Photo URLs. Use extensions such as .png, .jpg, .bmp, .wbmp, or .gif (still images only). Indeed displays images with a 3:2 aspect ratio at a standard size of 375 × 250 px and resizes and crops photos to fit. To post multiple images, separate the URLs with commas.

You can specify keywords and image URLs as comma-separated multiple values.
Indeed tests these new elements and rolls them out gradually, so Indeed does not guarantee that it displays every element you specify. Contact your assigned Alliance Manager for details.
When you add or modify existing or new elements, request that Indeed add the corresponding configuration on its side. Notify Indeed whenever you make changes.
Other notes
Japan only.
Update the feed at least once per day.
Make sure the XML feed content and the job detail page content match exactly.
Do not include test jobs, job board jobs, or shopping mall jobs.
Formatting guidelines (Japan)
Japan only.
To define job descriptions in the XML feed, include HTML formatting inside CDATA tags. Use the same HTML formatting in the CDATA tags that you use on your website.

Indeed normalizes HTML content and displays it to job seekers in a standardized format that does not strictly follow HTML standards.

Indeed does not support HTML entities. For example, use < instead of the HTML &lt; entity.

Indeed can reject HTML that does not follow these formatting guidelines or render it with formatting issues.

Indeed supports these HTML tags:

Formatting guidelines table
Tag	Description
<b>	Bold.
<h1>～<h6>

Headers.

Note: Indeed renders text in header tags at a consistent size on Indeed pages.

<br>	Single line break.
<p>	Paragraph. Indeed inserts blank lines between paragraph tags.
<ul>	Unordered list (bulleted list).
<li>	List item.
<strong>	Bold text.
<em>	Emphasized text (italic).
<table>、<tbody>、<th>、<tr>、<td>

Basic table. Indeed renders each cell with a line break.
Indeed also supports these computed style nodes:

Supported computed style nodes table
Node	Description
<font style="font-weight:bold">Some bold text</font>	Bold.
<div> <h2 style="display:inline">Label: </h2> Text </div>	
Displays inline text.

<h2> is a block tag by default.

Use positive numbers for margin and padding values above and below paragraph tags. This is the default behavior of <p> tags.

Formatting example
This example formats a job description:

English

<description>
  <![CDATA[
<h2 id="job_description">Job Description:<ul><li>Do you have 1-3 years of sales experience?</li><li> Are you relentless at closing the deal? </li><li>Are you ready for an exciting and high-speed career in sales? If so, we want to hear from you!</li></ul><font style="font-weight:bold">Benefits</font><p>We provide competitive compensation, including stock options and a full benefit plan. As a fast-growing business, we offer excellent opportunities for exciting and challenging work. As our company continues to grow, you can expect unlimited career advancement! </p>
]]>
</description>
Japanese

<description>
  <![CDATA[
<h2 id="job_description">仕事内容<ul><li>1～3年のセールスの経験をお持ちの方。</li><li> 取引成立に向けて全力で挑める方。 </li><li>セールス業界で、急成長を続ける活気に満ちた環境でのキャリアをお探しの方。連絡をお待ちしています。</li></ul><font style="font-weight:bold">福利厚生</font><p>ストックオプションや充実した福利厚生など、魅力的な給与体系が用意されています。急成長を続ける企業として、私たちは面白味があってやりがいを感じられる仕事の機会を提供しています。成長を続ける弊社内には、キャリアアップできるさまざまなチャンスがあります。</p>
]]>
</description>
Publish the XML feed
To publish and update your XML feed for Indeed, use one of these methods:

Provide an XML URL for Indeed to crawl.
Provide a client-hosted FTP or SFTP site for Indeed to access the feed.
Publish the file directly to an Indeed FTP server. Indeed recommends compressed files.
Important XML feed policy guidelines
Include all jobs from your clients' career pages in the XML feed.

If the XML feed does not include all jobs, Indeed might reject the feed or limit job visibility.

Include all job information that job seekers can see on your clients' websites.

For example, if a career site lists salary information, your XML feed must also include the <salary> element. If the career site does not list salary information, Indeed does not require it for indexing.

Use URLs that link to job detail pages where job seekers can confirm job details without signing in.

The XML feed must include only current, actively hiring roles.

Common issues
Indeed can reject your XML feed or hide your jobs from search results because of these common issues:

Incomplete data

If you omit required data from your XML feed, Indeed might not approve the feed for launch.
Incorrect special character encoding

Open the feed URL in your browser, view the source, and confirm that special characters such as brackets (<>) render correctly. Confirm that the feed uses an XML declaration with a character encoding such as UTF-8. The file must include a header that declares an encoding. You can use an encoding other than UTF-8, but UTF-8 is the most common. XML files must use the character ranges allowed by the XML standard.
Jobs are missing from the feed, or job counts differ between the feed and career sites

Include every job in the feed for each client. The feed must include everything you publish on the web.
Jobs do not have unique reference numbers and locations

Give every job a unique location, a unique reference number, and unique content. Otherwise, the job loses visibility on Indeed.
If you reuse a reference number in the XML, Indeed shows only the first occurrence.
Job posting for multiple locations

For a job at multiple locations, send one entry per location where the position is open.
Region‑wide postings do not reflect region‑wide jobs

Specify the location with at least three fields: <city>, <state>, and <country>.
If you omit these elements, the job does not receive organic visibility by default.
Job postings in multiple languages require a unique job for every language

To post the same job in multiple languages, create a unique job entry in the XML for each language.
Incomplete or empty job descriptions

Include all text related to the job. For example, required qualifications might live in a separate category in your database, but include it in the <description> field for Indeed.
Jobs that are scams or suspected scams

Indeed works to exclude suspected scams. Write clear, complete job descriptions. Clients must be legitimate companies, and the listed jobs must be open positions.
Outdated jobs

Do not include outdated or inactive jobs in the XML feed. When a job fills, remove it from the feed. If Indeed finds outdated or inactive jobs, Indeed can require you to correct the behavior to keep using your XML feed.
Job quality issues

If clients do not follow the Job Posting Standards, if jobs are missing required fields, or if jobs do not meet Indeed quality rules, Indeed can exclude those jobs from search results.
If clients have concerns about their postings, they can review Indeed Policies and contact the Employer Help Center.
These common errors can occur with XML job elements:

Common errors with XML job elements
Element	Common errors
<title>	
Includes extra text such as location, job type, shift, or catchphrases.

<title><![CDATA[ Sales ]]></title>

<title><![CDATA[ Work with top clients! 2 days off per week! Sales) ]]></title>

<date>	
Specifies a future date.

If this element specifies a future date, the job might not be visible.

 A future date.


<company>	
For subsidiaries or franchises that operate multiple stores under the same company, enter the business or brand name in the simplest form job seekers recognize immediately. Do not include phonetic readings.

(Example 1) For companies with a facility or salon name, enter that name. For Hair Salon XX operated by Corporation A:

<company><![CDATA[ Corporation A]]></company>

<company><![CDATA[ Hair Salon XX ]]></company>

(Example 2) Do not add parentheses to the company name.


<company><![CDATA[ Corporation A（Hair Salon XX） ]]></company>

<company><![CDATA[ Hair Salon XX ]]></company>

(Example 3) Japan only. Do not use abbreviations such as (株) or (有). Enter the official name only, without department names.


<company><![CDATA[ (株)A 関東事業部 ]]></company>

<company><![CDATA[ 株式会社 A ]]></company>

(Example 4) Japan only. Do not include phonetic readings.


<company><![CDATA[ 株式会社FREE (フリー) ]]></company>

<company><![CDATA[ 株式会社FREE ]]></company>

<city>, <streetaddress>

The <city> element holds only the city. The <streetaddress> element holds the full address, including street name and number.

English: For "1234 Sunny Lane, Phoenix, AZ 85003":


Japanese: 「東京都千代田区丸の内1-9-2グラントウキョウサウスタワー」の場合:


<city><![CDATA[ Phoenix ]]></city>
<streetaddress><![CDATA[1234 Sunny Lane, Phoenix, AZ 85003 ]]></streetaddress>

<city><![CDATA[ 1234 Sunny Lane, Phoenix, AZ 85003 ]]></city>

<station>	
Japan only. Use only the train station name. Put bus stop information in the <description> tag, because the content in <description> must match the content on the <url> page.


For example, for "Nearest Roppongi Station XX bus stop":


<station><![CDATA[ Nearest Roppongi Station XX bus stop ]]></station>

<station><![CDATA[ Roppongi Station ]]></station>

Note: if the location information is incorrect, Indeed cannot load the job location correctly.


<description>	
The content and order of the <description> element must match the page that the <url> element points to.

The Indeed search results page shows the plain-text version of the <description> element, including any information already covered by other elements in the XML feed.

Use HTML formatting.

<salary>	
The salary.

Put the salary breakdown, examples, and bonuses in the <description> element.

Example: if the salary varies by experience:


English:

<salary><![CDATA[ $16.00-$20.00 per hour]]></salary>

<salary><![CDATA[ $16.00-$17.00 per hour More than 5 years experience $18.00-$20.00 per hour]]></salary>

Japanese:

<salary><![CDATA[時給1,600～2,000円]]></salary>

<salary><![CDATA[時給1,600～1,700円、経験年数5年以上の場合：時給1,800～2,000円]]></salary>

Indeed can extract the salary from elements other than <salary>.

All elements	
If you rename an element (for example, reqid to requisition_id), contact your Client Success representative to update the mapping. If you are an ATS, contact Indeed. Add every element you use to every job. Add the element with a blank value, for example, <salary> </salary> or <salary />.

XML feed FAQ

Which client credentials do I use for Indeed Apply requests?


How do I authenticate POST requests for candidate applications to my ATS?



Which authentication method is used for POST requests from Indeed to ATS?


Which clients require configuring demographic questions?


Which screener question types does Indeed allow?


How do I test JSON screener questions?


How do I test end-to-end Indeed Apply flow?



How does Indeed define a duplicate application?



How often does Indeed index the feed?


Which metadata can I include in a feed?


Which jobs from the feed appear in Indeed search results?







Why does Indeed require a job URL for Indeed Apply?


Why does Indeed require an email for each job?



How do I define the same job in multiple languages?


How do I define the same job in multiple locations?


How do I define a state- or country-wide job?








How do I post a remote job?











How do I enable Indeed Apply on a subset of a client's jobs?



What XML element do I use for prefectures?


How can a job seeker complete their application on your site after Indeed Apply?


When is the X-Indeed-Signature header required?
