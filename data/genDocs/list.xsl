<?xml version="1.0" encoding="UTF-8"?>
<!--
[content.xml]
<text:p text:style-name="P14">{ListType}</text:p>
<table:table table:name="List" table:style-name="List">
  <table:table-column table:style-name="List.A"/>
  <table:table-header-rows>
    <table:table-row>
      <table:table-cell table:style-name="List.A1" office:value-type="string">
        <text:p text:style-name="Table_20_Heading">
          <text:span text:style-name="T4">{Header}</text:span>
        </text:p>
      </table:table-cell>
    </table:table-row>
  </table:table-header-rows>
  <table:table-row>
    <table:table-cell table:style-name="List.A2" office:value-type="string">
      <text:p text:style-name="P17">{Value}</text:p>
    </table:table-cell>
  </table:table-row>
</table:table>

[data]
<list>
  <title>User's List</title>
  <cols>
    <col>User's name</col>
    <col>Email</col>
  </cols>
  <data>
    <row>
      <Name>User1</Name>
      <Email>mail1@mail.com</Email>
    </row> 
    <row>
      <Name>User2</Name>
      <Email>mail2@mail.com</Email>
    </row> 
  <data>
</list>
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
  <xsl:template match="text()[.='{ListType}']">
    <xsl:value-of select="$data//title"/>
  </xsl:template>

  <!--
  Because the number of cols is dynamic, we have to set the value
  -->
  <!-- Case 1 : the attribute is defined, update the value -->
  <xsl:template match="table:table[@table:name='List']/table:table-column/@table:number-columns-repeated/text()">
    <xsl:value-of select='count($data/list/cols/col)'/>
  </xsl:template>
  <!-- Case 2 : the attribute is NOT defined, add it -->
  <xsl:template match="table:table[@table:name='List']/table:table-column[not(@table:number-columns-repeated)]">
    <xsl:variable name="nCols" select="count($data/list/cols/col)"/>
    <table:table-column table:number-columns-repeated="">
      <xsl:attribute name="table:number-columns-repeated"><xsl:value-of select="count($data/list/cols/col)"/></xsl:attribute>      
      <xsl:apply-templates select="@* | node()"/>
    </table:table-column>
  </xsl:template>

  <!-- 
  TABLE'S HEADER
  We first need to identify the row where the header and then create so many cells
  as columns we have 
  -->
  <xsl:template match="table:table[@table:name='List']/table:table-header-rows/table:table-row/table:table-cell">
    <!-- 
    This contains the element 
      <table:table-cell>...</table:table-cell> 
    that acts as template 
    -->
    <xsl:variable name="template" select='.'/>

    <!-- 
    Now, create so many copies of that template as cols we have defined. 
    That will create the header with all the columns we need 
    -->
    <xsl:for-each select="$data//list/cols/col">
      <!-- Process first row template -->
      <xsl:apply-templates select="$template" mode="repeatLevel1">
        <xsl:with-param name="params" select="."/>
        <xsl:with-param name="ind" select="position()"/>
      </xsl:apply-templates>
    </xsl:for-each>
  </xsl:template>

  <!-- 
  TABLE'S CONTENTS
  Create so may rows in the table as list/data/row we have  
  -->
  <xsl:template match="table:table[@table:name='List']/table:table-row">
    <!-- 
    This contains the element 
      <table:table-row>...</table:table-row> 
    that acts as template 
    -->
    <xsl:variable name="template" select='.'/>

    <!-- Clone the row -->
    <xsl:for-each select="$data//list/data/row">
      <xsl:apply-templates select="$template" mode="repeatLevel1">
        <xsl:with-param name="params" select="."/>
        <xsl:with-param name="ind" select="position()"/>
      </xsl:apply-templates>
    </xsl:for-each>
  </xsl:template>

  <!-- Ignore row (representing a template), already processed before -->  
  <!-- ??  
  <xsl:template match="table:table[@table:name='TResultsByPoll']/table:table-row[3]"></xsl:template>
  -->

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
  <xsl:template match="text()[.='{Header}']" mode="repeatLevel1">
    <xsl:param name="params"/>

    <xsl:value-of select='$params/text()'/>
  </xsl:template>

  <!-- 
  A table's content's row 
  Create so many cells as cols we have
  -->
  <xsl:template match="table:table[@table:name='List']/table:table-row/table:table-cell" mode="repeatLevel1">
    <xsl:param name="params"/>
    <xsl:param name="ind"/>

    <!-- template : <table:table-cell>...</table:table-cell> -->
    <xsl:variable name="template" select='.'/>

    <!-- 
    Now, create so many copies of that template as cols we have defined. 
    That will create the header with all the columns we need 
    -->
    <xsl:for-each select="$params/*">
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
  <!-- A value in a table's content row -->
  <xsl:template match="text()[.='{Value}']" mode="repeatLevel2">
    <xsl:param name="params"/>

    <xsl:value-of select='$params/text()'/>
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
