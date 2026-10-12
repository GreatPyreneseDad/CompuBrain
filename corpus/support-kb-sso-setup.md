---
title: "Support KB - Setting Up Single Sign-On"
source: support-kb
scope: public
---
# Support KB - Setting Up Single Sign-On

This article explains how to configure SAML 2.0 single sign-on (SSO) between Ridgeline and your identity provider (IdP). It covers Okta and Microsoft Entra ID, required attribute mapping, testing, and common errors. Ridgeline supports SSO on the Fleet, Brokerage, and Enterprise plans. Your Ridgeline admin must enable SSO before the steps below will work.

## Before you start

You need:

- A Ridgeline account owner or admin role.
- Admin access to your IdP tenant.
- A test user in your IdP who is not your main admin account. Use this user to validate the connection before you enforce SSO for everyone.

Plan a short window for the change. Existing users with password logins can keep signing in until you turn on enforcement in step 5 of the testing section.

## Values to give your IdP

Ridgeline acts as the service provider (SP). Your IdP will ask for these values:

| Setting | Value |
|---|---|
| Single sign-on URL (ACS URL) | https://app.kestrelridge.com/saml/acs |
| Audience URI (SP Entity ID) | https://app.kestrelridge.com/saml/metadata |
| Name ID format | EmailAddress |
| Application username | Email |
| Response and assertion | Signed |
| Signing algorithm | RSA-SHA256 |

You can also download the Ridgeline SP metadata XML from Settings > Security > SSO. Upload it to your IdP if the IdP supports metadata import.

## Setting up Okta

1. In the Okta Admin Console, go to Applications > Create App Integration.
2. Choose SAML 2.0 and click Next.
3. Enter "Ridgeline" as the app name and upload the Ridgeline logo if you want.
4. Enter the ACS URL and Audience URI from the table above.
5. Set Name ID format to EmailAddress and Application username to Email.
6. Add the attribute statements listed in the attribute mapping section.
7. Finish the wizard. On the Sign On tab, click View SAML setup instructions.
8. Copy the Identity Provider Single Sign-On URL, the IdP Issuer, and download the X.509 certificate. You will enter these in Ridgeline.
9. Assign the app to your test user, then to your pilot group.

## Setting up Microsoft Entra ID

1. In the Entra admin center, go to Enterprise applications > New application > Create your own application.
2. Choose "Integrate any other application you don't find in the gallery" and name it "Ridgeline."
3. Open Single sign-on and select SAML.
4. In Basic SAML Configuration, enter the Identifier (Entity ID) and Reply URL (ACS URL) from the table above.
5. Under Attributes & Claims, confirm that the NameID source is user.mail, or user.userprincipalname if your tenant uses UPN as the sign-in name.
6. Add the claims in the attribute mapping section.
7. In SAML Certificates, download the Certificate (Base64) and copy the Login URL and Microsoft Entra Identifier.
8. Under Users and groups, assign your test user, then your pilot group.

## Attribute mapping

Ridgeline reads these attributes from the SAML assertion:

- `email` (required): the user's sign-in address. Must match the email on the Ridgeline user record.
- `firstName` and `lastName` (recommended): used for display names in audit logs.
- `groups` (optional): maps IdP groups to Ridgeline roles. Each group name must match a role mapping set in Settings > Security > SSO > Group Mapping.

Attribute names are case-sensitive. Use the exact spelling above. Okta and Entra both allow custom attribute names, so check the spelling after you save.

## Testing your connection

1. In Ridgeline, go to Settings > Security > SSO and enter the IdP Login URL, Issuer or Entity ID, and certificate. Save, but leave enforcement off.
2. Open a private browser window and go to https://app.kestrelridge.com/login. Click "Sign in with SSO" and enter the test user's email.
3. Confirm you land in the correct Ridgeline account and that your name and role appear correctly.
4. Check Settings > Security > SSO > Login Activity. A successful login shows the NameID and the assertion ID.
5. After the pilot user works for 24 hours, set SSO to "Required for all users" and save. Keep one break-glass admin with a password login in case the IdP is unavailable. Store those credentials outside your IdP.

## Common errors and fixes

**"Signature validation failed."** The certificate in Ridgeline does not match the IdP's current signing certificate. Re-download the certificate from the IdP and upload it again. Certificates often rotate on a yearly schedule.

**"Audience restriction mismatch."** The Audience URI in the IdP does not match the Ridgeline SP Entity ID. Copy it again from the table above, with no trailing slash.

**"No user found with email."** The `email` attribute is missing or does not match the Ridgeline user record. Check the attribute name and that the user's email is the same in both systems.

**"Assertion expired" or "Clock skew."** The IdP and Ridgeline clocks differ by more than five minutes. Check the IdP's time settings. Ridgeline does not allow adjustment.

**"User not assigned to application."** The user is not in the IdP app assignment. Add them to the app or to an assigned group.

If none of these fix the problem, send the Login Activity entry, the time of the attempt in UTC, and the IdP name to support@kestrelridge.com. Do not send certificates or passwords.
