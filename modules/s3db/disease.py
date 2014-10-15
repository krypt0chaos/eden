# -*- coding: utf-8 -*-

__all__ = ("DiseaseDataModel",
           "CaseTrackingModel",
           "ContactTracingModel",
           "disease_rheader",
           )

from gluon import *
from gluon.storage import Storage
from ..s3 import *
from s3layouts import S3AddResourceLink

# =============================================================================
class DiseaseDataModel(S3Model):

    names = ("disease_disease",
             "disease_disease_id",
             "disease_symptom",
             "disease_symptom_id",
             )

    def model(self):
        
        T = current.T
        db = current.db

        crud_strings = current.response.s3.crud_strings

        define_table = self.define_table
        
        # =====================================================================
        # Basic Disease Information
        #
        tablename = "disease_disease"
        table = define_table(tablename,
                             Field("name"),
                             Field("short_name"),
                             Field("code",
                                   label = T("ICD-10-CM Code"),
                                   ),
                             Field("description", "text"),
                             s3_comments(),
                             *s3_meta_fields())

        represent = S3Represent(lookup=tablename)
        disease_id = S3ReusableField("disease_id", "reference %s" % tablename,
                                     label = T("Disease"),
                                     represent = represent,
                                     requires = IS_ONE_OF(db, "disease_disease.id",
                                                          represent,
                                                          ),
                                     sortby = "name",
                                     comment = S3AddResourceLink(f="disease",
                                                                 tooltip=T("Add a new disease to the catalog"),
                                                                 ),
                                     )

        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Create Disease"),
            title_display = T("Disease Information"),
            title_list = T("Diseases"),
            title_update = T("Edit Disease Information"),
            title_upload = T("Import Disease Information"),
            label_list_button = T("List Diseases"),
            label_delete_button = T("Delete Disease Information"),
            msg_record_created = T("Disease Information added"),
            msg_record_modified = T("Disease Information updated"),
            msg_record_deleted = T("Disease Information deleted"),
            msg_list_empty = T("No Diseases currently registered"))

        self.add_components(tablename,
                            disease_symptom = "disease_id",
                            )

        # =====================================================================
        # Symptom Information
        #
        tablename = "disease_symptom"
        table = define_table(tablename,
                             disease_id(),
                             Field("name"),
                             Field("description",
                                   label = T("Short Description"),
                                   ),
                             Field("assessment",
                                   label = T("Assessment method"),
                                   ),
                             *s3_meta_fields())

        # @todo: refine to include disease name?
        represent = S3Represent(lookup=tablename)
        symptom_id = S3ReusableField("symptom_id", "reference %s" % tablename,
                                     label = T("Symptom"),
                                     represent = represent,
                                     requires = IS_ONE_OF(db, "disease_symptom.id",
                                                          represent,
                                                          ),
                                     sortby = "name",
                                     )
                                     
        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Add Symptom"),
            title_display = T("Symptom Information"),
            title_list = T("Symptoms"),
            title_update = T("Edit Symptom Information"),
            title_upload = T("Import Symptom Information"),
            label_list_button = T("List Symptoms"),
            label_delete_button = T("Delete Symptom Information"),
            msg_record_created = T("Symptom Information added"),
            msg_record_modified = T("Symptom Information updated"),
            msg_record_deleted = T("Symptom Information deleted"),
            msg_list_empty = T("No Symptom Information currently available"))

        # Pass names back to global scope (s3.*)
        return dict(disease_disease_id = disease_id,
                    disease_symptom_id = symptom_id,
                    )

    # -------------------------------------------------------------------------
    @staticmethod
    def defaults():
        """ Safe defaults for names in case the module is disabled """

        dummy = S3ReusableField("dummy_id", "integer",
                                readable = False,
                                writable = False)

        return dict(disease_disease_id = lambda **attr: dummy("disease_id"),
                    disease_symptom_id = lambda **attr: dummy("symptom_id"),
                    )

# =============================================================================
class CaseTrackingModel(S3Model):

    names = ("disease_case",
             "disease_case_id",
             "disease_case_status",
             )

    def model(self):
        
        T = current.T
        db = current.db

        crud_strings = current.response.s3.crud_strings

        define_table = self.define_table
        
        person_id = self.pr_person_id

        # =====================================================================
        # Case
        #
        tablename = "disease_case"
        table = define_table(tablename,
                             person_id(),
                             self.disease_disease_id(),
                             *s3_meta_fields())

        represent = S3Represent(lookup=tablename, fields=["person_id"])
        case_id = S3ReusableField("case_id", "reference %s" % tablename,
                                  label = T("Case"),
                                  represent = represent,
                                  requires = IS_ONE_OF(db, "disease_case.id",
                                                       represent,
                                                       ),
                                  comment = S3AddResourceLink(f="case",
                                                              tooltip=T("Add a new case"),
                                                              ),
                                  )

        self.add_components(tablename,
                            disease_case_status = "case_id",
                            disease_contact = "case_id",
                            )

        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Create Case"),
            title_display = T("Case Details"),
            title_list = T("Cases"),
            title_update = T("Edit Cases"),
            title_upload = T("Import Cases"),
            label_list_button = T("List Cases"),
            label_delete_button = T("Delete Case"),
            msg_record_created = T("Case added"),
            msg_record_modified = T("Case updated"),
            msg_record_deleted = T("Case deleted"),
            msg_list_empty = T("No Cases currently registered"))

        # =====================================================================
        # Status
        #
        tablename = "disease_case_status"
        table = define_table(tablename,
                             case_id(),
                             # @todo: add basic status information fields
                             s3_date(),
                             # @todo: add inline-component for symptoms
                             *s3_meta_fields())
                             
        # @todo: add symptom component
        # @todo: add custom CRUD form

        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Add Status Update"),
            title_display = T("Status Update"),
            title_list = T("Status Updates"),
            title_update = T("Edit Status Update"),
            title_upload = T("Import Status Updates"),
            label_list_button = T("List Status Updates"),
            label_delete_button = T("Delete Status Update"),
            msg_record_created = T("Status Update added"),
            msg_record_modified = T("Status Update updated"),
            msg_record_deleted = T("Status Update deleted"),
            msg_list_empty = T("No Status Information currently available"))


        # =====================================================================
        # Status <=> Symptom
        #
        tablename = "disease_case_status_symptom"
        table = define_table(tablename,
                             # @todo: status_id
                             # @todo: symptom_id
                             *s3_meta_fields())

        # @todo: CRUD strings

        # Pass names back to global scope (s3.*)
        return dict(disease_case_id = case_id)

    # -------------------------------------------------------------------------
    @staticmethod
    def defaults():

        return dict()

# =============================================================================
class ContactTracingModel(S3Model):

    names = ("disease_contact",
             "disease_contact_person",
             )

    def model(self):
        
        T = current.T
        db = current.db

        crud_strings = current.response.s3.crud_strings

        define_table = self.define_table

        person_id = self.pr_person_id

        # =====================================================================
        # Contact: place/time when a people were in contact with a case
        #
        
        # Status of the tracing
        contact_tracing_status = {
            "OPEN": T("Open"),         # not all contact persons identified yet
            "COMPLETE": T("Complete"), # all contact persons identified
        }
        tablename = "disease_contact"
        table = define_table(tablename,
                             self.disease_case_id(label="Source Case"),
                             s3_datetime("start_date",
                                         label = T("From"),
                                         widget = S3DateTimeWidget(set_min="disease_contact_end_date",
                                                                   ),
                                         ),
                             s3_datetime("end_date",
                                         label = T("To"),
                                         widget = S3DateTimeWidget(set_max="disease_contact_start_date",
                                                                   ),
                                         ),
                             self.gis_location_id(),
                             Field("status",
                                   label = T("Tracing Status"),
                                   requires = IS_IN_SET(contact_tracing_status),
                                   represent = S3Represent(options=contact_tracing_status),
                                   ),
                             *s3_meta_fields())
                             
        represent = S3Represent(lookup=tablename, fields=["person_id", "date"])
        contact_id = S3ReusableField("contact_id", "reference %s" % tablename,
                                     label = T("Contact"),
                                     represent = represent,
                                     requires = IS_ONE_OF(db, "disease_contact.id",
                                                          represent,
                                                          ),
                                     sortby = "date",
                                     comment = S3AddResourceLink(f="contact",
                                                                 tooltip=T("Add a new contact"),
                                                                 ),
                                     )

        self.add_components(tablename,
                            disease_contact_person = "contact_id",
                            )

        # CRUD strings
        crud_strings[tablename] = Storage(
            label_create = T("Register Contact Tracing"),
            title_display = T("Contact Tracing Information"),
            title_list = T("Contact Tracings"),
            title_update = T("Edit Contact Tracing"),
            title_upload = T("Import Contact Tracing"),
            label_list_button = T("List Contact Tracings"),
            label_delete_button = T("Delete Contact Tracing"),
            msg_record_created = T("Contact Tracing registered"),
            msg_record_modified = T("Contact Tracing updated"),
            msg_record_deleted = T("Contact Tracing deleted"),
            msg_list_empty = T("No Contact Tracings currently registered"))

        # =====================================================================
        # Contact Person: persons who've been involved in a contact
        #
        tablename = "disease_contact_person"
        table = define_table(tablename,
                             contact_id(),
                             person_id(),
                             s3_datetime(),
                             *s3_meta_fields())

        crud_strings[tablename] = Storage(
            label_create = T("Add Contact Person"),
            title_display = T("Contact Person Details"),
            title_list = T("Contact Persons"),
            title_update = T("Edit Contact Person"),
            title_upload = T("Import Contact Persons"),
            label_list_button = T("List Contact Persons"),
            label_delete_button = T("Delete Contact Person"),
            msg_record_created = T("Contact Person added"),
            msg_record_modified = T("Contact Person Details updated"),
            msg_record_deleted = T("Contact Person deleted"),
            msg_list_empty = T("No Contact Persons currently registered"))

        # Pass names back to global scope (s3.*)
        return dict()

    # -------------------------------------------------------------------------
    @staticmethod
    def defaults():

        return dict()

# =============================================================================
def disease_rheader(r, tabs=None):
    
    T = current.T
    if r.representation != "html":
        return None

    resourcename = r.name

    if resourcename == "disease":

        tabs = [(T("Basic Details"), None),
                (T("Symptoms"), "symptom"),
                ]
               
        rheader_fields = [["name"],
                          ["code"],
                          ]
        rheader = S3ResourceHeader(rheader_fields, tabs)(r)
        
    elif resourcename == "case":

        tabs = [(T("Basic Details"), None),
                (T("Status"), "status"),
                (T("Contacts"), "contact"),
                ]

        rheader_fields = [["person_id"],
                          ]
        rheader = S3ResourceHeader(rheader_fields, tabs)(r)

    elif resourcename == "contact":

        tabs = [(T("Basic Details"), None),
                (T("Contact Persons"), "contact_person"),
                ]

        rheader_fields = [["case_id"],
                          ]
        rheader = S3ResourceHeader(rheader_fields, tabs)(r)

    return rheader

# END =========================================================================
