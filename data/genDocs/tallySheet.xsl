<?xml version="1.0" encoding="UTF-8"?>
<!--
[content.xml]

        <table:table table:name="CONTEST" table:style-name="CONTEST">
            <table:table-column table:style-name="CONTEST.A"/>
            <table:table-row>
                <table:table-cell table:style-name="CONTEST.A1" office:value-type="string">
                    <table:table table:name="QUESTIONS" table:style-name="QUESTIONS">
                        <table:table-column table:style-name="QUESTIONS.A" table:number-columns-repeated="2"/>
                        <table:table-header-rows>
                            <table:table-row>
                                <table:table-cell table:style-name="QUESTIONS.A1" office:value-type="string">
                                    <text:p text:style-name="Table_20_Heading"/>
                                </table:table-cell>
                                <table:table-cell table:style-name="QUESTIONS.B1" office:value-type="string">
                                    <text:p text:style-name="Table_20_Heading"/>
                                </table:table-cell>
                            </table:table-row>
                        </table:table-header-rows>
                        <table:table-row>
                            <table:table-cell table:style-name="QUESTIONS.A2" office:value-type="string">
                                <text:p text:style-name="P9"/>
                            </table:table-cell>
                            <table:table-cell table:style-name="QUESTIONS.B2" office:value-type="string">
                                <text:p text:style-name="P9"/>
                            </table:table-cell>
                        </table:table-row>
                    </table:table>
                    <text:p text:style-name="P9"/>
                </table:table-cell>
            </table:table-row>
        </table:table>
[data]

<tallySheet>
  <title>TallySheet</title>
  <data>
    <contests>
      <row>
        <contestId>256</contestId>
        <contestName>Best food in Africa</contestName>
        <contestOrden>2</contestOrden>
        <options>
          <row>
            <optionId>34</optionId>
            <optionName>Dish #1 in  Africa</optionName>
            <optionOrden>1</optionOrden>
          </row>
          <row>
            <optionId>27</optionId>
            <optionName>Dish #2 in  Africa</optionName>
            <optionOrden>2</optionOrden>
          </row>
          ...
        </options>
      </row>
      <row>
        <contestId>1</contestId>
        <contestName>Best movie in Algeria</contestName>
        <contestOrden>3</contestOrden>
        <options>
          <row>
            <optionId>1061</optionId>
            <optionName>Movie #1 in  Algeria</optionName>
            <optionOrden>1</optionOrden>
          </row>
          <row>
            <optionId>806</optionId>
            <optionName>Movie #2 in  Algeria</optionName>
            <optionOrden>2</optionOrden>
          </row>
          .....
        </options>
      </row>
      ...
    </contests>
  </data>
</tallySheet>
-->
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
>
  <xsl:output method="xml"/>

  <!-- The file with the data we are going to put in the document -->
  <xsl:param name="fData"/>
  <xsl:variable name="data" select="document($fData)"/>

  <!-- ======================================================
  main (aka. repeatLevel0)
  The main rules, not inside any repeated element
  ======================================================= -->
  <!-- List's title -->
  <xsl:template match="text()[.='{Title}']">
    <xsl:value-of select="$data/tallySheet/title"/>
  </xsl:template>

  <!-- 
  CONTEST
  Create so may blocks as contests we have  
  -->
  <xsl:template match="text:section[@text:name='CONTEST']">
    <xsl:variable name="template" select='.'/>

    <!-- Clone the row -->
    <xsl:for-each select="$data/tallySheet/data/contests/row">
      <xsl:apply-templates select="$template" mode="repeatLevel1">
        <xsl:with-param name="params" select="."/>
        <xsl:with-param name="ind" select="position()"/>
      </xsl:apply-templates>
    </xsl:for-each>
  </xsl:template>

  <!-- Default copy rule -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- ======================================================
  repeatLevel1
  Repeated elements created by a template inside repeatLevel0
  ======================================================= -->
  <!-- A table's header name -->
  <xsl:template match="text()[.='{ContestName}']" mode="repeatLevel1">
    <xsl:param name="params"/>

    <xsl:value-of select='$params/contestName'/>
  </xsl:template>

  <!-- 
  A table's content's row 
  Create so many rows as questions we have
  -->
  <xsl:template match="table:table[@table:name='ANSWER']" mode="repeatLevel1">
    <xsl:param name="params"/>
    <xsl:param name="ind"/>

    <xsl:variable name="template" select='.'/>

    <!-- 
    So many rows as questions
    -->
    <xsl:for-each select="$params/options/row">
      <!-- Process first row template -->
      <xsl:apply-templates select="$template" mode="repeatLevel2">
        <xsl:with-param name="params" select="."/>
        <xsl:with-param name="ind" select="position()"/>
      </xsl:apply-templates>
    </xsl:for-each>
  </xsl:template>

  <!-- Default copy rule -->
  <xsl:template match="@*|node()" mode="repeatLevel1">
    <xsl:param name="params"/>
    <xsl:param name="ind"/>

    <xsl:copy>
      <xsl:apply-templates select="@*|node()" mode="repeatLevel1">
        <xsl:with-param name="params" select="$params"/>
        <xsl:with-param name="ind" select="$ind"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <!-- ======================================================
  repeatLevel2
  Repeated elements created by a template inside repeatLevel1
  ======================================================= -->
  <!-- A question's answer -->
  <xsl:template match="text()[.='{Answer}']" mode="repeatLevel2">
    <xsl:param name="params"/>

    <xsl:value-of select='$params/optionName'/>
  </xsl:template>

  <!-- Default copy rule -->
  <xsl:template match="@*|node()" mode="repeatLevel2">
    <xsl:param name="params"/>
    <xsl:param name="ind"/>

    <xsl:copy>
      <xsl:apply-templates select="@*|node()" mode="repeatLevel2">
        <xsl:with-param name="params" select="$params"/>
        <xsl:with-param name="ind" select="$ind"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
