<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:fn="fn" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="clinical_study">
		<xsl:text>NCT ID&#x9;Recruitment&#x9;Interventions&#x9;Start Date&#x9;Completion Date&#x9;Primary Completion Date&#x9;Phase&#x9;Countries&#10;</xsl:text>
		<xsl:value-of select="./id_info/nct_id" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./overall_status" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./intervention/intervention_type" separator=": " /><xsl:text>:&#x9;</xsl:text>
		<xsl:value-of select="./start_date" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./completion_date" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./primary_completion_date" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./phase" /><xsl:text>&#x9;</xsl:text>
		<xsl:value-of select="./location_countries/country" separator="| "/>
	</xsl:template>
</xsl:stylesheet>
