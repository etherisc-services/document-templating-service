# Quote Template: {{ quote.quoteNumber || 'Q2025000003' }}

## Participants

| # | Description | Property |
|---|-------------|----------|
{%tr for item in participants %}
| {{ loop.index }} | Id | {{ item.id }} |
|  | Participant Role | {{ item.role }} |
|  | Is Active | {{ item.isActive }} |
|  | Sum Insured | {{ item.sumInsured }} |
|  | Payment Details | {{ item.paymentDetails }} |
|  | Bulk Upload Id | {{ item.bulkUploadId }} |
|  | Bulk Upload Row Index | {{ item.bulkUploadRowIndex }} |
|  | Farmer | {{ item.farmer }} |
|  | Is Policyholder | {{ item.isPolicyholder }} |
|  | Is Insured | {{ item.isInsured }} |
|  | Is From Bulk Upload | {{ item.isFromBulkUpload }} |
|  | Has Payment Details | {{ item.hasPaymentDetails }} |
{%tr endfor %}

## Quote

| Description | Property |
|-------------|----------|
| Quote ID | {{ quote.id }} |
| Quote Number | {{ quote.quoteNumber }} |
| Template Name | {{ quote.templateName }} |
| Status | {{ quote.status }} |
| Notes | {{ quote.notes }} |
| Strike Level | {{ quote.strikeLevel }} |
| Sum Insured | {{ quote.sumInsured }} |
| Premium Amount | {{ quote.premiumAmount }} |
| Selected Scenarios | {{ quote.selectedScenarios }} |
| Calculation Results | {{ quote.calculationResults }} |
| Quotation Job Id | {{ quote.quotationJobId }} |
| Current Wizard Step | {{ quote.currentWizardStep }} |
| Approved At | {{ quote.approvedAt }} |
| Approved By | {{ quote.approvedBy }} |
| Rejected Reason | {{ quote.rejectedReason }} |
| Created By | {{ quote.createdBy }} |
| Updated By | {{ quote.updatedBy }} |
| Product Id | {{ quote.productId }} |
| Organization Id | {{ quote.organizationId }} |

### Coverage Start Date

### Coverage End Date

### Underlying Assets

#### Activities_products

| # | Description | Property |
|---|-------------|----------|
{%tr for item in quote.underlyingAssets.activities_products %}
| {{ loop.index }} | Type | {{ item.type }} |
{%tr endfor %}

### Perils Config

| Description | Property |
|-------------|----------|
| Total_weight_check | {{ quote.perilsConfig.total_weight_check }} |

#### Perils

| # | Description | Property |
|---|-------------|----------|
{%tr for item in quote.perilsConfig.perils %}
| {{ loop.index }} | Weight | {{ item.weight }} |
|  | Peril_id | {{ item.peril_id }} |
{%tr endfor %}

### Location Validation

| Description | Property |
|-------------|----------|
| Validated_at | {{ quote.locationValidation.validated_at }} |
| Total_locations | {{ quote.locationValidation.total_locations }} |
| Valid_locations | {{ quote.locationValidation.valid_locations }} |
| Coverage_area_used | {{ quote.locationValidation.coverage_area_used }} |
| All_within_coverage | {{ quote.locationValidation.all_within_coverage }} |
| Validation_performed | {{ quote.locationValidation.validation_performed }} |

#### Invalid_locations

| # | Description | Property |
|---|-------------|----------|
{%tr for item in quote.locationValidation.invalid_locations %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

### Protection Levels

#### Excess

| Description | Property |
|-------------|----------|
| Units | {{ quote.protectionLevels.excess.units }} |
| Strike_level | {{ quote.protectionLevels.excess.strike_level }} |
| Strike_value | {{ quote.protectionLevels.excess.strike_value }} |
| Exhaust_level | {{ quote.protectionLevels.excess.exhaust_level }} |
| Exhaust_value | {{ quote.protectionLevels.excess.exhaust_value }} |

#### Deficit

| Description | Property |
|-------------|----------|
| Units | {{ quote.protectionLevels.deficit.units }} |
| Strike_level | {{ quote.protectionLevels.deficit.strike_level }} |
| Strike_value | {{ quote.protectionLevels.deficit.strike_value }} |
| Exhaust_level | {{ quote.protectionLevels.deficit.exhaust_level }} |
| Exhaust_value | {{ quote.protectionLevels.deficit.exhaust_value }} |

### Quotation Results

| Description | Property |
|-------------|----------|
| Job_id | {{ quote.quotationResults.job_id }} |
| Status | {{ quote.quotationResults.status }} |
| Message | {{ quote.quotationResults.message }} |
| Success | {{ quote.quotationResults.success }} |
| Job_type | {{ quote.quotationResults.job_type }} |
| Progress | {{ quote.quotationResults.progress }} |
| Timestamp | {{ quote.quotationResults.timestamp }} |
| Created_at | {{ quote.quotationResults.created_at }} |
| Started_at | {{ quote.quotationResults.started_at }} |
| Updated_at | {{ quote.quotationResults.updated_at }} |
| Completed_at | {{ quote.quotationResults.completed_at }} |
| Error_details | {{ quote.quotationResults.error_details }} |

#### Input

| Description | Property |
|-------------|----------|
| Loading | {{ quote.quotationResults.input.loading }} |
| Tax Rate | {{ quote.quotationResults.input.taxRate }} |
| Job_type | {{ quote.quotationResults.input.job_type }} |
| Api_version | {{ quote.quotationResults.input.api_version }} |
| Num_farmers | {{ quote.quotationResults.input.num_farmers }} |
| Subsidy Rate | {{ quote.quotationResults.input.subsidyRate }} |
| Insured_data | {{ quote.quotationResults.input.insured_data }} |
| Perils_config | {{ quote.quotationResults.input.perils_config }} |
| Coverage Limits | {{ quote.quotationResults.input.coverageLimits }} |
| Coverage End Date | {{ quote.quotationResults.input.coverageEndDate }} |
| Quotation_script | {{ quote.quotationResults.input.quotation_script }} |
| Coverage Start Date | {{ quote.quotationResults.input.coverageStartDate }} |
| Coverage_period_days | {{ quote.quotationResults.input.coverage_period_days }} |
| Estimated_processing_time_minutes | {{ quote.quotationResults.input.estimated_processing_time_minutes }} |

#### Output

##### Metadata

| Description | Property |
|-------------|----------|
| Git_commit | {{ quote.quotationResults.output.metadata.git_commit }} |
| Farmers_count | {{ quote.quotationResults.output.metadata.farmers_count }} |
| Coverage_period | {{ quote.quotationResults.output.metadata.coverage_period }} |
| Quotation_script | {{ quote.quotationResults.output.metadata.quotation_script }} |
| Calculation_timestamp | {{ quote.quotationResults.output.metadata.calculation_timestamp }} |
| Processing_time_seconds | {{ quote.quotationResults.output.metadata.processing_time_seconds }} |

##### Quotation_result

| # | Description | Property |
|---|-------------|----------|
{%tr for item in quote.quotationResults.output.quotation_result %}
| {{ loop.index }} | Data | {{ item.data }} |
|  | Farmer I D | {{ item.farmerID }} |
|  | Latitude | {{ item.latitude }} |
|  | Longitude | {{ item.longitude }} |
|  | Sum Insured | {{ item.sumInsured }} |
{%tr endfor %}

#### Control_flags

| Description | Property |
|-------------|----------|
| Timeout_at | {{ quote.quotationResults.control_flags.timeout_at }} |
| Pause_requested | {{ quote.quotationResults.control_flags.pause_requested }} |
| Cancel_requested | {{ quote.quotationResults.control_flags.cancel_requested }} |

### Farm Data

| Description | Property |
|-------------|----------|
| Wizard_created | {{ quote.farmData.wizard_created }} |

### Risk Assessment

| Description | Property |
|-------------|----------|
| Status | {{ quote.riskAssessment.status }} |

### Coverage Period

| Description | Property |
|-------------|----------|
| Status | {{ quote.coveragePeriod.status }} |

### Valid Until

### Created At

### Updated At

### Coverage Items

| # | Description | Property |
|---|-------------|----------|
{%tr for item in quote.coverageItems %}
| {{ loop.index }} | Type | {{ item.type }} |
|  | Selected | {{ item.selected }} |
{%tr endfor %}

## Helpers

| Description | Property |
|-------------|----------|
| Is Master Policy | {{ helpers.isMasterPolicy }} |
| Is Individual Policy | {{ helpers.isIndividualPolicy }} |
| Is Draft | {{ helpers.isDraft }} |
| Is Template | {{ helpers.isTemplate }} |
| Is Proposal | {{ helpers.isProposal }} |
| Is Under Review | {{ helpers.isUnderReview }} |
| Is Approved | {{ helpers.isApproved }} |
| Is Executed | {{ helpers.isExecuted }} |
| Is Rejected | {{ helpers.isRejected }} |
| Is Expired | {{ helpers.isExpired }} |
| Has Results | {{ helpers.hasResults }} |
| Has Quotation Results | {{ helpers.hasQuotationResults }} |
| Has Calculation Results | {{ helpers.hasCalculationResults }} |
| Has Protection Levels | {{ helpers.hasProtectionLevels }} |
| Has Perils Config | {{ helpers.hasPerilsConfig }} |
| Has Location Validation | {{ helpers.hasLocationValidation }} |
| Has Coverage Items | {{ helpers.hasCoverageItems }} |
| Participant Count | {{ helpers.participantCount }} |
| Has Participants | {{ helpers.hasParticipants }} |
| Has Policyholder | {{ helpers.hasPolicyholder }} |
| Has Insured Participants | {{ helpers.hasInsuredParticipants }} |
| Coverage Duration Days | {{ helpers.coverageDurationDays }} |
| Is Expired Quote | {{ helpers.isExpiredQuote }} |
| Days Until Expiry | {{ helpers.daysUntilExpiry }} |
| Is Wizard In Progress | {{ helpers.isWizardInProgress }} |
| Wizard Completion Percentage | {{ helpers.wizardCompletionPercentage }} |
| Total Premium Amount | {{ helpers.totalPremiumAmount }} |
| Total Sum Insured | {{ helpers.totalSumInsured }} |
| Has Financial Data | {{ helpers.hasFinancialData }} |

## Product

| Description | Property |
|-------------|----------|
| Id | {{ product.id }} |
| Product Name | {{ product.name }} |
| Product Code | {{ product.code }} |
| Product Version | {{ product.version }} |
| Product Status | {{ product.status }} |
| Organization Id | {{ product.organizationId }} |
| Is Active | {{ product.isActive }} |
| Is Paused | {{ product.isPaused }} |
| Is Archived | {{ product.isArchived }} |
| Is Draft | {{ product.isDraft }} |
| Has Pricing Factors | {{ product.hasPricingFactors }} |
| Has Product Config | {{ product.hasProductConfig }} |
| Tag Count | {{ product.tagCount }} |

### Product Config

#### Loading Config

| Description | Property |
|-------------|----------|
| Tax Rate | {{ product.productConfig.loadingConfig.taxRate }} |
| Subsidy Rate | {{ product.productConfig.loadingConfig.subsidyRate }} |

##### Peril Weighting

| Description | Property |
|-------------|----------|
| Enforcement | {{ product.productConfig.loadingConfig.perilWeighting.enforcement }} |

###### Weights

####### Drought

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.perilWeighting.weights.drought.max }} |
| Min | {{ product.productConfig.loadingConfig.perilWeighting.weights.drought.min }} |

####### Excess-rain-flooding

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.perilWeighting.weights.excess-rain-flooding.max }} |
| Min | {{ product.productConfig.loadingConfig.perilWeighting.weights.excess-rain-flooding.min }} |

##### Coverage Level Limits

| Description | Property |
|-------------|----------|
| Enforcement | {{ product.productConfig.loadingConfig.coverageLevelLimits.enforcement }} |

###### Limits

####### Drought

######## Strike

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.drought.strike.max }} |
| Min | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.drought.strike.min }} |

######## Exhaust

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.drought.exhaust.max }} |
| Min | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.drought.exhaust.min }} |

####### Excess-rain-flooding

######## Strike

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.excess-rain-flooding.strike.max }} |
| Min | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.excess-rain-flooding.strike.min }} |

######## Exhaust

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.excess-rain-flooding.exhaust.max }} |
| Min | {{ product.productConfig.loadingConfig.coverageLevelLimits.limits.excess-rain-flooding.exhaust.min }} |

##### Loading Factors

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.loadingConfig.loadingFactors %}
| {{ loop.index }} | Admin Level | {{ item.adminLevel }} |
|  | Admin Unit Id | {{ item.adminUnitId }} |
|  | Admin Unit Code | {{ item.adminUnitCode }} |
|  | Admin Unit Name | {{ item.adminUnitName }} |
{%tr endfor %}

#### Coverage Config

| Description | Property |
|-------------|----------|
| Currency | {{ product.productConfig.coverageConfig.currency }} |

##### Sum Insured Limits

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.coverageConfig.sumInsuredLimits.max }} |
| Min | {{ product.productConfig.coverageConfig.sumInsuredLimits.min }} |

##### Coverage Period Limits

| Description | Property |
|-------------|----------|
| Type | {{ product.productConfig.coverageConfig.coveragePeriodLimits.type }} |

###### End Date Range

| Description | Property |
|-------------|----------|
| Latest | {{ product.productConfig.coverageConfig.coveragePeriodLimits.endDateRange.latest }} |
| Earliest | {{ product.productConfig.coverageConfig.coveragePeriodLimits.endDateRange.earliest }} |

###### Start Date Range

| Description | Property |
|-------------|----------|
| Latest | {{ product.productConfig.coverageConfig.coveragePeriodLimits.startDateRange.latest }} |
| Earliest | {{ product.productConfig.coverageConfig.coveragePeriodLimits.startDateRange.earliest }} |

##### Coverage Level Global Limits

###### Drought

####### Strike

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.drought.strike.max }} |
| Min | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.drought.strike.min }} |

####### Exhaust

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.drought.exhaust.max }} |
| Min | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.drought.exhaust.min }} |

###### Excess-rain-flooding

####### Strike

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.excess-rain-flooding.strike.max }} |
| Min | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.excess-rain-flooding.strike.min }} |

####### Exhaust

| Description | Property |
|-------------|----------|
| Max | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.excess-rain-flooding.exhaust.max }} |
| Min | {{ product.productConfig.coverageConfig.coverageLevelGlobalLimits.excess-rain-flooding.exhaust.min }} |

##### Perils

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.coverageConfig.perils %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

##### Area Options

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.coverageConfig.areaOptions %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

##### Activities Or Products

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.coverageConfig.activitiesOrProducts %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

#### Pricing Factors

| Description | Property |
|-------------|----------|
| Subsidy Rate | {{ product.productConfig.pricingFactors.subsidyRate }} |
| Minimum Premium | {{ product.productConfig.pricingFactors.minimumPremium }} |
| Administrative Fee | {{ product.productConfig.pricingFactors.administrativeFee }} |
| Agent Commission Rate | {{ product.productConfig.pricingFactors.agentCommissionRate }} |
| Underwriting Loading | {{ product.productConfig.pricingFactors.underwritingLoading }} |
| Broker Commission Rate | {{ product.productConfig.pricingFactors.brokerCommissionRate }} |

#### Stakeholders Anrp Distribution

##### Administration

###### Insurer

| Description | Property |
|-------------|----------|
| Name | {{ product.productConfig.stakeholdersAnrpDistribution.administration.insurer.name }} |
| Role | {{ product.productConfig.stakeholdersAnrpDistribution.administration.insurer.role }} |
| Percentage | {{ product.productConfig.stakeholdersAnrpDistribution.administration.insurer.percentage }} |
| Organization Id | {{ product.productConfig.stakeholdersAnrpDistribution.administration.insurer.organizationId }} |

###### Myubuntu

| Description | Property |
|-------------|----------|
| Name | {{ product.productConfig.stakeholdersAnrpDistribution.administration.myubuntu.name }} |
| Role | {{ product.productConfig.stakeholdersAnrpDistribution.administration.myubuntu.role }} |
| Percentage | {{ product.productConfig.stakeholdersAnrpDistribution.administration.myubuntu.percentage }} |
| Organization Id | {{ product.productConfig.stakeholdersAnrpDistribution.administration.myubuntu.organizationId }} |

##### Brokers

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.stakeholdersAnrpDistribution.brokers %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

##### Underwriters

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.stakeholdersAnrpDistribution.underwriters %}
| {{ loop.index }} | Name | {{ item.name }} |
|  | Is Insurer | {{ item.isInsurer }} |
|  | Percentage | {{ item.percentage }} |
|  | Organization Id | {{ item.organizationId }} |
{%tr endfor %}

##### Calculating Agents

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.stakeholdersAnrpDistribution.calculatingAgents %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

##### Other Organisations

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.productConfig.stakeholdersAnrpDistribution.otherOrganisations %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

### Created At

### Updated At

### Tags

| # | Description | Property |
|---|-------------|----------|
{%tr for item in product.tags %}
| {{ loop.index }} | Item | {{ item }} |
{%tr endfor %}

## Organization

| Description | Property |
|-------------|----------|
| Id | {{ organization.id }} |
| Organization Name | {{ organization.name }} |
| Organization Code | {{ organization.code }} |
| Organization Type | {{ organization.type }} |
| Settings | {{ organization.settings }} |
| Is Active | {{ organization.isActive }} |

## Users

| Description | Property |
|-------------|----------|
| Approved By | {{ users.approvedBy }} |

### Created By

| Description | Property |
|-------------|----------|
| Id | {{ users.createdBy.id }} |
| Name | {{ users.createdBy.name }} |
| Email | {{ users.createdBy.email }} |

### Updated By

| Description | Property |
|-------------|----------|
| Id | {{ users.updatedBy.id }} |
| Name | {{ users.updatedBy.name }} |
| Email | {{ users.updatedBy.email }} |

---

*This template was generated automatically and uses Jinja2 syntax for dynamic content.*
