# Formance

This page guides you through the process of setting up the Formance source connector.

## Set up the Formance connector 

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Formance** from the Source type dropdown.
4. Enter a name for your source.
5. For **Start date**, enter the date in RFC3339 format (the format is inclusive, for example, "2023-01-02T15:04:01Z" includes the first second of 4th minute). The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
6. Enter your Oauth Client id and secret to authenticate your account.
7. Click **Set up source**.

## Supported sync modes

The Formance source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

 - Full Refresh
 - Incremental

## Supported Streams

The Formance source connector supports the following streams:

* [Accounts](https://docs.formance.com/api/stack/v1.0#tag/Accounts/operation/listAccounts) \(Full table\)
* [Balances](https://docs.formance.com/api/stack/v1.0#tag/Balances/operation/getBalances) \(Full table\)
* [Transactions](https://docs.formance.com/api/stack/v1.0#tag/Transactions/operation/listTransactions) \(Incremental\)


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                       |
|:--------| :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| 0.1.0   | 2023-XX-XX | [XXXX](https://github.com/airbytehq/airbyte/pull/XXXX)   | Release Formance CDK Connector                                                                |
