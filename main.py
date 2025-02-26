"""
Single-file plugin for Horizon that adds 'My Panel' to 'Project' dashboard.
Allows start/stop/delete, usage, snapshot for instances via openstacksdk.
Place it in openstack_dashboard/local/enabled/ and restart Horizon.
"""

from django.urls import path
from django.http import HttpResponse, HttpResponseRedirect
import horizon
import openstack

DASHBOARD='project'
PANEL='my_panel'
PANEL_GROUP='default'
ADD_PANEL='my_onefile_plugin.MyPanel'

class MyPanel(horizon.Panel):
    name='My Panel'
    slug='my_panel'
    def get_urls(self):
        return [
            path('',self.index,name='index'),
            path('start/<server_id>/',self.start,name='start'),
            path('stop/<server_id>/',self.stop,name='stop'),
            path('delete/<server_id>/',self.delete,name='delete'),
            path('usage/<server_id>/',self.usage,name='usage'),
            path('snapshot/<server_id>/',self.snapshot,name='snapshot'),
        ]
    def index(self,request):
        try:
            conn=openstack.connection.Connection()
            servers=list(conn.compute.servers())
            h='<h2>My Instances</h2><ul>'
            for s in servers:
                h+=f"<li>{s.name}({s.status}) "
                h+=f"<a href='start/{s.id}'>start</a>|<a href='stop/{s.id}'>stop</a>|<a href='delete/{s.id}'>del</a>"
                h+=f"|<a href='usage/{s.id}'>usage</a>|<a href='snapshot/{s.id}'>snap</a></li>"
            h+='</ul>'
            return HttpResponse(h)
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    def start(self,request,server_id):
        conn=openstack.connection.Connection()
        s=conn.compute.get_server(server_id)
        if s:
            conn.compute.start_server(s)
        return HttpResponseRedirect('../')
    def stop(self,request,server_id):
        conn=openstack.connection.Connection()
        s=conn.compute.get_server(server_id)
        if s:
            conn.compute.stop_server(s)
        return HttpResponseRedirect('../')
    def delete(self,request,server_id):
        conn=openstack.connection.Connection()
        s=conn.compute.get_server(server_id)
        if s:
            conn.compute.delete_server(s)
        return HttpResponseRedirect('../')
    def usage(self,request,server_id):
        conn=openstack.connection.Connection()
        s=conn.compute.get_server(server_id)
        if not s:
            return HttpResponse("No instance.")
        u={'vCPUs':s.flavor.vcpus,'RAM':s.flavor.ram,'Disk':s.flavor.disk}
        return HttpResponse(f"<pre>{u}</pre>")
    def snapshot(self,request,server_id):
        conn=openstack.connection.Connection()
        s=conn.compute.get_server(server_id)
        if not s:
            return HttpResponse("No instance.")
        try:
            image=conn.compute.create_server_image(s,name=f"snap_{s.name}")
            if image:
                image=conn.image.wait_for_image(image)
                return HttpResponse(f"Snapshot created: {image.id} ({image.status})")
        except Exception as e:
            return HttpResponse(f"Error: {e}")
        return HttpResponse("Snapshot creation failed.")
