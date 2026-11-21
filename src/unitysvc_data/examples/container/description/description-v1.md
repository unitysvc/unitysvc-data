## Using container services on UnitySVC

A container service runs software in an instance for your enrollment. You can
use it briefly, on demand or continuously. This page lists the service's
capabilities, channels, prices and application-specific instructions; the steps
below apply to container services generally.

### Enroll and configure

1. Sign in and [enroll](?topic=enrollment) in the service.
2. Choose a [channel](?topic=channel). It determines the container sizes and
   available settings. Check its price and resource requirements before enrolling.
3. Review the enrollment parameters and save your configuration. Defaults may
   generate application keys or tokens; keep the generated values or supply your
   own as the application guide directs.

UnitySVC passes these parameters to the software. The application handles its
own authentication; UnitySVC adds no application security gate or built-in
instance key. An application key is separate from your UnitySVC account/API key.

### Start and connect

Start the instance from your enrollment and wait for it to become ready. Open an
entry URL shown in the instance details, then follow the application's guide for
login, first-use steps or client configuration.

Use the instance's entry URLs to reach the software. A container service is not
called through the API gateway's service path, and different applications expose
different web interfaces or APIs. An application may have public endpoints as
well as endpoints that require its own credentials.

### Runtime and cost

Check the selected channel's [price](?topic=pricing) and your
[wallet](?topic=wallet). Container services can have different seller prices;
do not assume that every service is free or priced at platform cost.

A running instance incurs runtime charges even while idle. Keep it running for
continuous use, or start and stop it when needed. Closing a browser tab or client
does not stop the instance. Compute charges for that run end when the instance
has stopped; stopping does not erase charges already incurred.

### Storage and configuration changes

Treat storage inside the instance as temporary. A container restart can retain
scratch data, but stopping or replacing the instance loses it. Save anything
important outside the instance, using storage supported by the application.
Long-term use does not itself provide persistent storage or backups.

Changing enrollment parameters may restart or replace the instance. Read the
application guide before changing settings that affect credentials or stored data.

### Stop and start again

Use **Stop** in the instance controls and wait for the instance to show that it
has stopped. You can start it again later under the enrollment, with fresh
temporary storage and the saved parameter values. Follow the application's setup
steps again if its login state or other local data was lost.

If startup fails or an entry does not respond, check the instance status and the
application's requirements, parameters and chosen size. A local Docker test does
not establish that a platform size is sufficient. Contact the seller with the
reported error; do not post application keys or tokens in support messages.
